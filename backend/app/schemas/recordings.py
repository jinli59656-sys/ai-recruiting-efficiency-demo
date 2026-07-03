from datetime import datetime, date
from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field, ConfigDict


#上传录音
class UploadRecordingForm(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resume_id:int
    position_id:int|None=Field(default=None,alias="positionId",description="关联岗位id")
    interview_date:date|None=Field(default=None,alias="interviewDate")
    interviewer:str|None=Field(default=None,description="面试官")

#更新文字稿
class RecordingUpdateTranscript(BaseModel):
    transcript:str




#响应参数
#上传录音
class UploadRecordingResponse(BaseModel):
    id:int
    file_name:str
    duration:Optional[int]
    duration_text:Optional[str]
    transcript_status:int
    transcript_status_name:str

# 开始转写
class StartTranscriptResponse(BaseModel):
    id:int
    transcript_status:int
    transcript_status_name:str
    estimated_time:str

#获取录音详情
class RecordingDetailResponse(BaseModel):
    id:int
    candidate_name:str
    duration:Optional[int]
    transcript_status_name:Optional[str]
    transcript:Optional[str]
    transcript_error:Optional[str]
    interviewer:Optional[str]
    interview_date:Optional[date]
    created_at:datetime

#获取录音列表
class RecordingListResponse(BaseModel):
    total:int
    page:int
    page_size:int
    results:list[RecordingDetailResponse]

#获取录音状态
class RecordingStatusResponse(BaseModel):
    id:int
    status:str

#获取录音文字稿
class RecordingTranscriptResponse(BaseModel):
    id:int
    transcript_status_name:str
    transcript:str
    word_count:int
    updated_at:str

