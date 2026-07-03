from datetime import datetime, date

from sqlalchemy.orm import Session

from app.models.recordings import InterviewRecording



def create_recording(db:Session,resume_id:int,position_id:int|None,
                     file_name:str,file_path:str,file_type:str,file_size:int,
                     duration:int|None,interviewer:str|None,interview_date:date|None):
    db_recording=InterviewRecording(
        resume_id=resume_id,position_id=position_id,file_name=file_name,
        file_path=file_path,file_type=file_type,file_size=file_size,duration=duration,transcript_status=0,interviewer=interviewer,
        interview_date=interview_date
    )
    db.add(db_recording)
    db.flush()
    return db_recording

def get_recording_by_id(recording_id:int,db:Session):
    db_recording=db.query(InterviewRecording).filter(InterviewRecording.id==recording_id).first()
    return db_recording

#更改状态
def update_recording_transcript_status(recording_id:int,transcript_status:int,db:Session):
    db_recording=get_recording_by_id(recording_id,db)
    if not db_recording:
        return None
    db_recording.transcript_status=transcript_status
    return db_recording

#保存转写结果
def save_transcript_result(recording_id:int,transcript:str,db:Session):
    db_recording = get_recording_by_id(recording_id, db)
    if not db_recording:
        return None

    db_recording.transcript = transcript
    db_recording.transcript_status = 2
    db_recording.transcript_error = None
    return db_recording

#保存失败信息
def save_transcript_error(recording_id:int,error_message:str,db:Session):
    db_recording=get_recording_by_id(recording_id,db)
    if not db_recording:
        return None
    db_recording.transcript_status=3
    db_recording.transcript_error=error_message

    return db_recording

#获取录音列表
def get_recordings_list(page:int,page_size:int,db:Session):
    query =db.query(InterviewRecording) #先看下有多少条数据，query.count()
    total=query.count()
    db_recordings =query.offset((page-1)*page_size).limit(page_size).all()
    if not db_recordings:
        return None
    return total,db_recordings

#更新文字稿
def update_transcript(id:int,transcript:str,db:Session):
    db_recording=get_recording_by_id(id,db)
    if not db_recording:
        return None
    db_recording.transcript=transcript
    db.flush()
    return db_recording

#删除录音
def remove_recording(id:int,db:Session):
    db_recording =db.query(InterviewRecording).filter(InterviewRecording.id==id).first()
    if not db_recording:
        return None
    db.delete(db_recording)
    return db_recording

def get_recording_by_resume_position_id(resume_id:int,position_id:int,db:Session):
    db_recording=db.query(InterviewRecording).filter(InterviewRecording.resume_id==resume_id,
                                        InterviewRecording.position_id==position_id).first()
    return db_recording