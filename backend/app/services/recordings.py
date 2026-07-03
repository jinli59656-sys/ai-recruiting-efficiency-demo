import tempfile
import wave
import json
from http import HTTPStatus
from io import BytesIO
from pathlib import Path
import subprocess
import dashscope
from dashscope.audio.asr import Recognition
from openai import OpenAI
from mutagen import File as MutagenFile
from fastapi import UploadFile, HTTPException, BackgroundTasks

from sqlalchemy.orm import Session
from starlette import status

from app.crud.position import get_position_by_id
from app.crud.recordings import create_recording, get_recording_by_id, save_transcript_result, save_transcript_error
from app.crud.resume import get_resume_by_id
from app.schemas.recordings import UploadRecordingForm, UploadRecordingResponse, StartTranscriptResponse
from app.storage.minio_storage import upload_recording_file, download_recording_file
from config import settings
from database import SessionLocal

ALLOWED_SUFFIXES={".mp3",".wav",".m4a",".aac"}

CONTENT_TYPE_MAP = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac"
  }

MAX_FILE_SIZE_MAP = {
    ".mp3": 200 * 1024 * 1024,
    ".wav": 500 * 1024 * 1024,
    ".m4a": 200 * 1024 * 1024,
    ".aac": 200 * 1024 * 1024,
}

TRANSCRIPT_STATUS_NAME_MAP = {
    0: "未转写",
    1: "转写中",
    2: "已完成",
    3: "失败"
}





def process_recording_upload(file:UploadFile,form_data:UploadRecordingForm,db:Session):
    #1.先校验resume
    db_resume=get_resume_by_id(db,form_data.resume_id)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="关联简历不存在")
    #2.如果传了position_id,再校验岗位
    if form_data.position_id is not None:
        db_position=get_position_by_id(form_data.position_id,db)
        if not db_position:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联岗位不存在")

    #3. 文件名和后缀
    file_name=file.filename or ""
    suffix=Path(file_name).suffix.lower()

    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="不支持的录音格式")

    #4. 读文件字节
    file_bytes=file.file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="上传文件不能为空")

    #5. 校验文件大小
    file_size=len(file_bytes)
    max_size=MAX_FILE_SIZE_MAP[suffix]
    if file_size>max_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="文件大小超出限制")

    #6. 上传到minio
    object_name=upload_recording_file(file_bytes=file_bytes,file_name=file_name,content_type=CONTENT_TYPE_MAP.get(suffix))

    #7. 计算时长
    duration=get_audio_duration(file_bytes=file_bytes,suffix=suffix)
    duration_text=format_duration(duration) if duration is not None else None

    #8.写数据库
    file_type = suffix.replace(".", "")
    db_recording=create_recording(
        db=db,
        resume_id=form_data.resume_id,
        position_id=form_data.position_id if form_data.position_id is not None else None,
        file_name=file_name,
        file_path=object_name,
        file_type=file_type,
        file_size=file_size,
        duration=duration,
        interviewer=form_data.interviewer,
        interview_date=form_data.interview_date
    )

    db.commit()
    db.refresh(db_recording)

    return UploadRecordingResponse(
        id=db_recording.id,
        file_name=db_recording.file_name,
        duration=db_recording.duration,
        duration_text=duration_text,
        transcript_status=db_recording.transcript_status,
        transcript_status_name=TRANSCRIPT_STATUS_NAME_MAP.get(db_recording.transcript_status,"未知")
    )

#时长格式化函数
def format_duration(duration:int|None):
    if duration is None:
        return None
    minutes=duration//60
    seconds=duration%60

    return f"{minutes:02d}:{seconds:02d}"

#得到时长
def get_audio_duration(file_bytes, suffix:str):
    try:
        if suffix ==".wav":
            with wave.open(BytesIO(file_bytes),"rb") as wav_file:
                frames=wav_file.getnframes()
                frame_rate=wav_file.getframerate()
                if frame_rate ==0:
                    print("wav frame_rate=0，无法计算时长")
                    return None
                return int(frames/frame_rate)

        return get_audio_duration_by_ffprobe(file_bytes, suffix)
    except Exception:
        print(f"获取音频时长失败，suffix={suffix}, error={e}")
        return None


def get_audio_duration_by_ffprobe(file_bytes: bytes, suffix: str):
    with tempfile.TemporaryDirectory(prefix="audio_probe_") as temp_dir:
        temp_file_path = Path(temp_dir) / f"temp{suffix}"
        temp_file_path.write_bytes(file_bytes)

        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(temp_file_path)
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode != 0:
            raise Exception(result.stderr or "ffprobe 执行失败")

        duration_str = result.stdout.strip()
        if not duration_str:
            return None

        return int(float(duration_str))

#开始转写
def start_transcription(recording_id:int,background_task:BackgroundTasks,db:Session):
    db_recording=get_recording_by_id(recording_id,db)
    if not db_recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该录音不存在")
    #得到了录音就开始判断状态、更新状态、启动后台任务
    if db_recording.transcript_status==1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="该录音正在转写中，请勿重复提交")

    if db_recording.transcript_status==2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该录音已完成转写")

    #更新状态为转写中
    db_recording.transcript_status=1
    db_recording.transcript_error=None
    db.commit()
    db.refresh(db_recording)

    #启动后台任务
    background_task.add_task(transcribe_recording_task,recording_id)

    #返回响应
    return StartTranscriptResponse(
        id=db_recording.id,
        transcript_status=db_recording.transcript_status,
        transcript_status_name=TRANSCRIPT_STATUS_NAME_MAP.get(db_recording.transcript_status,"未知"),
        estimated_time=estimate_transcription_time(db_recording.duration,db_recording.file_size)
    )




#后台转写任务
def transcribe_recording_task(recording_id:int):
    #1.根据id查找录音
    db=SessionLocal()
    try:
        db_recording = get_recording_by_id(recording_id, db)
        if not db_recording:
            return
        # 2.下载minio的录音文件
        #2.1 先将文件下载到临时文件夹
        with tempfile.TemporaryDirectory(prefix="recording_transcribe_") as temp_dir:
            local_file_path=Path(temp_dir)/db_recording.file_name

            download_recording_file(
                object_name=db_recording.file_path,
                target_path=str(local_file_path)
            )

            # 3.调ASR，语音转文字模型
            #用的是fun-asr-realtime 但是此模型不支持m4a，所以要将其转为wav格式，此模型转文字不限制录音文件大小和时间
            #3.1准备格式 ---直接将所有格式都转为wav
            asr_file_path,asr_file_type=prepare_audio_for_asr(
                str(local_file_path),
                db_recording.file_type
            )
            #下面这个是直接转写，不分多人
            transcript=transcribe_audio_file(asr_file_path,asr_file_type)

            #优化：多人转写
            # raw_sentences=transcribe_audio_file_with_speakers(asr_file_path,asr_file_type)
            # #将得到的结果格式化
            # sentences=normalize_speaker_sentences(raw_sentences)
            # #将结果转化为str并且带有结构，可以直接存入mysql  --transcript方便人看
            # transcript=build_multi_speaker_transcript(sentences)
            # #将结构化文本放入，方便程序理解
            # transcript_json=json.dumps(sentences,ensure_ascii=False)

        # 4.更新数据库状态
        save_transcript_result(recording_id,transcript,db)
        db.commit()
    except Exception as e:
        db.rollback()
        save_transcript_error(recording_id,str(e),db)
        db.commit()
    finally:
        db.close()

#计算转写时间，先按照时长，时长不行按照大小
def estimate_transcription_time(duration:int |None,file_size:int|None):
    if duration is not None:
        if duration <= 5 * 60:
            return "约1分钟"
        if duration <= 15 * 60:
            return "约3分钟"
        if duration <= 30 * 60:
            return "约5分钟"
        if duration <= 60 * 60:
            return "约10分钟"
        return "约15分钟"

    if file_size is not None:
        mb=file_size/(1024*1024)
        if mb<=5:
            return "约1分钟"
        if mb<=20:
            return "约3分钟"
        if mb<=50:
            return "约5分钟"
        return "约10分钟"

    return "约5分钟"


#将录音格式转换为wav
def prepare_audio_for_asr(local_file_path:str,file_type:str):
    """
    给录音的路径和类型，转化为wav类型
    """
    wav_file_path=str(Path(local_file_path).with_suffix(".wav"))

    convert_audio_to_wav(local_file_path,wav_file_path)

    return wav_file_path,"wav"

def convert_audio_to_wav(source_path:str,target_path:str):
    """
    转成
    wav、pcm_s16le、16khz、单声道
    """
    command=[
        "ffmpeg","-y","-i",source_path,
        "-acodec","pcm_s16le" #参数是转成 PCM 16-bit little-endian，最常见的ASR友好格式
        ,"-ar","16000" #采样率转为16khz
        ,"-ac","1" #单声道
        ,target_path
    ]
    result=subprocess.run(command,capture_output=True,text=True,encoding="utf-8",errors="ignore")

    if result.returncode!=0:
        raise Exception(f"音频转换失败：{result.stderr}")

#后台转写任务，分多人格式
# def transcribe_audio_file_with_speakers(file_path:str,file_type:str):
#     return [
#         {"speaker_id": 0, "text": "你好，请先做个自我介绍。"},
#         {"speaker_id": 1, "text": "好的，我叫张三，毕业于某某大学。"},
#         {"speaker_id": 0, "text": "你上一份工作主要负责什么？"},
#         {"speaker_id": 1, "text": "我主要负责后端开发和接口设计。"},
#     ]
#
# def normalize_speaker_sentences(raw_sentences):
#     if not raw_sentences:
#         return []
#
#     normlized=[]
#
#     for item in raw_sentences:
#         if not isinstance(item,dict):
#             continue
#
#         speaker_id=item.get("speaker_id",item.get("speakerId",0))
#         text=item.get("text",item.get("sentence",""))
#
#         text=str(text).strip()
#         if not text:
#             continue
#
#         normlized.append(
#             {
#                 "speaker_id":int(speaker_id),
#                 "text":text
#             }
#         )
#     return normlized
#
# def build_multi_speaker_transcript(sentences:list[dict]):
#     if not sentences:
#         return ""
#     lines=[]
#     for item in sentences:
#         speaker_id=item.get("speaker_id",0)
#         text=item.get("text","").strip()
#
#         if not text:
#             continue
#
#         lines.append(f"说话人{speaker_id+1}:{text}")
#
#     return "\n".join(lines)

#为什么不用qwen3-asr-model呢 --qwen不支持直接传文件，且限制时长＜5，大小 ＜10MB
def transcribe_audio_file(file_path:str,file_type:str):
    dashscope.api_key=settings.QWEN_API_KEY
    dashscope.base_websocket_api_url="wss://dashscope.aliyuncs.com/api-ws/v1/inference"

    sample_rate=16000

    recognition=Recognition(
        model=settings.FUN_ASR_MODEL,
        format=file_type,
        sample_rate=sample_rate,
        callback=None
    )

    result=recognition.call(file_path)

    if result.status_code!=HTTPStatus.OK:
        raise Exception(f"ASR调用失败：{result.message}")
    #得到的是列表，结构化数据
    sentence_result=result.get_sentence()
    #需要提取为文本
    transcript = extract_transcript_text(sentence_result)
    if not transcript:
        raise Exception("ASR返回空结果")
    return transcript.strip()


def extract_transcript_text(sentence_result):
    """
        将result转化为str并返回，本身可能是str、list、dict
    """
    if not sentence_result:
        return ""
    if isinstance(sentence_result, str):
        return sentence_result.strip()

    if isinstance(sentence_result, dict):
        return str(sentence_result.get("text", "")).strip()

    if isinstance(sentence_result, list):
        parts = []
        for item in sentence_result:
            if isinstance(item, dict):
                text = str(item.get("text", "")).strip()
                if text:
                    parts.append(text)
            elif isinstance(item, str):
                text = item.strip()
                if text:
                    parts.append(text)

        return "".join(parts).strip()

    return str(sentence_result).strip()



#将str的字符数得到
def get_word_count(transcript:str |None):
    if not transcript:
        return 0
    return len("".join(transcript.split()))




