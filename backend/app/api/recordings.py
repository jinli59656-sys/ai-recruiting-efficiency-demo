from datetime import date
from pathlib import Path

from Crypto.SelfTest.Cipher.test_OFB import file_name
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import StreamingResponse

from app.services.recordings import process_recording_upload,start_transcription,TRANSCRIPT_STATUS_NAME_MAP
from app.database import get_db
from app.schemas.recordings import UploadRecordingForm,RecordingDetailResponse,RecordingListResponse,RecordingUpdateTranscript
from app.utils.response import success_response
from app.crud.recordings import get_recording_by_id,get_recordings_list,update_transcript
from app.crud.resume import get_resume_by_id
from crud.recordings import remove_recording
from schemas.recordings import RecordingStatusResponse, RecordingTranscriptResponse
from services.recordings import get_word_count, CONTENT_TYPE_MAP
from storage.minio_storage import delete_resume_file, get_recording_file_stream

router=APIRouter(prefix="/api/v1/recordings",tags=["录音管理模块"])



#上传录音
@router.post("/upload",summary="上传录音")
def upload_recordings(file:UploadFile=File(...,description="音频文件"),
                      resume_id:int =Form(...,description="关联候选人ID"),
                      position_id:int|None=Form(default=None,description="关联岗位ID"),
                      interview_date:date|None=Form(default=None,description="面试日期"),
                      interviewer:str|None=Form(default=None,description="面试官姓名"),
                      db:Session=Depends(get_db)):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="请上传录音文件")

    form_data=UploadRecordingForm(
        resume_id=resume_id,position_id=position_id,interview_date=interview_date,interviewer=interviewer
    )

    result= process_recording_upload(
        file=file,
        form_data=form_data,
        db=db
    )

    return success_response(message="上传录音成功",data=result)

@router.get("/{id}/stream",summary="播放录音")
def stream_recording(id:int,db:Session=Depends(get_db)):
    db_recording=get_recording_by_id(id,db)
    if not db_recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="录音不存在")

    object_name=db_recording.file_path
    file_name=db_recording.file_name

    file_stream=get_recording_file_stream(object_name)

    suffix=Path(file_name).suffix.lower()
    media_type=CONTENT_TYPE_MAP.get(suffix,"application/octet-stream")

    return StreamingResponse(
        file_stream,
        media_type=media_type
    )


@router.post("/{id}/transcribe",summary="开始转写")
def start_transcript(id:int,background_tasks:BackgroundTasks,db:Session=Depends(get_db)):
    #转写是异步的，这里只是发起任务
    result=start_transcription(
        recording_id=id,
        background_task=background_tasks,
        db=db
    )

    return success_response(message="开始转写",data=result)

@router.get("/{id}",summary="获取录音详情")
def get_recording_retail(id:int,db:Session=Depends(get_db)):
    db_recording=get_recording_by_id(id,db)
    if not db_recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该录音不存在")
    db_resume=get_resume_by_id(db,db_recording.resume_id)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该简历不存在")
    result=RecordingDetailResponse(
        id=db_recording.id,
        candidate_name=db_resume.candidate_name,
        duration=db_recording.duration,
        transcript_status_name=TRANSCRIPT_STATUS_NAME_MAP.get(db_recording.transcript_status,"unknown"),
        transcript=db_recording.transcript,
        transcript_error=db_recording.transcript_error,
        interviewer=db_recording.interviewer,
        interview_date=db_recording.interview_date,
        created_at=db_recording.created_at
    )
    return success_response(message="获取录音详情成功",data=result)

@router.get("",summary="获取录音列表")
def get_recording_list(page:int=Query(1,ge=1,description="页码"),
                       page_size:int=Query(10,ge=1,le=50,description="每页数量"),
                       db:Session=Depends(get_db)):
    total,db_recordings=get_recordings_list(page,page_size,db)
    if not db_recordings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="查找不到录音")

    results=[]
    for db_recording in db_recordings:
        db_resume=get_resume_by_id(db,db_recording.resume_id)
        if not db_resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该简历不存在")
        result =RecordingDetailResponse(
            id=db_recording.id,
            candidate_name=db_resume.candidate_name,
            duration=db_recording.duration,
            transcript_status_name=TRANSCRIPT_STATUS_NAME_MAP.get(db_recording.transcript_status, "unknown"),
            transcript=db_recording.transcript,
            transcript_error=db_recording.transcript_error,
            interviewer=db_recording.interviewer,
            interview_date=db_recording.interview_date,
            created_at=db_recording.created_at
        )
        results.append(result)
    data=RecordingListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=results
    )
    return success_response(message="获取录音列表成功",data=data)

@router.get("/{id}/status",summary="获取转写状态")
def get_recording_status(id:int,db:Session=Depends(get_db)):
    db_recording=get_recording_by_id(id,db)
    if not db_recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该录音不存在")
    status=TRANSCRIPT_STATUS_NAME_MAP.get(db_recording.transcript_status,"unknown")
    data=RecordingStatusResponse(id=id,status=status)
    return success_response(message="获取状态成功",data=data)

@router.get("/{id}/transcript",summary="获取文字稿")
def get_recording_transcript(id:int,db:Session=Depends(get_db)):
    db_recording =get_recording_by_id(id,db)
    if not db_recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该录音不存在")
    transcript=db_recording.transcript
    word_count=get_word_count(transcript)
    data=RecordingTranscriptResponse(
        id=id,
        transcript_status_name=TRANSCRIPT_STATUS_NAME_MAP.get(db_recording.transcript_status,"unknown"),
        transcript=transcript,
        word_count=word_count,
        updated_at=str(db_recording.updated_at)
    )
    return success_response(message="获取文字稿成功",data=data)

@router.put("/{id}/transcript",summary="更新文字稿")
def update_recording_transcript(id:int,data:RecordingUpdateTranscript,db:Session=Depends(get_db)):
    db_recording=update_transcript(id,data.transcript,db)
    if not db_recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该录音不存在")
    db.commit()
    db.refresh(db_recording)
    transcript = db_recording.transcript
    word_count = get_word_count(transcript)
    result=RecordingTranscriptResponse(
        id=id,
        transcript_status_name=TRANSCRIPT_STATUS_NAME_MAP.get(db_recording.transcript_status, "unknown"),
        transcript=transcript,
        word_count=word_count,
        updated_at=str(db_recording.updated_at)
    )
    return success_response(message="更新文字稿成功",data=result)

@router.delete("/{id}",summary="删除录音")
def delete_recording(id:int,db:Session=Depends(get_db)):
    db_recording=remove_recording(id,db)

    if not db_recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="录音本身不存在")
    db.commit()
    delete_resume_file(db_recording.file_path)
    return success_response(message="录音删除成功")