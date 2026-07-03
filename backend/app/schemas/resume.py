from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, Field

from app.schemas.resume_parse import WorkExperienceItem, ProjectExperienceItem, EducationExperienceItem

class ResumeListRequest(BaseModel):
    keyword:Optional[str]=None
    position_id:Optional[int]=Field(None,alias="positionId")
    education:Optional[str]=None
    work_years_min:Optional[int]=Field(None,alias="workYearsMin")
    work_years_max:Optional[int]=Field(None,alias="workYearsMax")
    status:Optional[int]=None
    page:int=1
    page_size:int=10


#批量下载的请求体
class ResumeBatchDownloadRequest(BaseModel):
    ids:List[int]

#更改简历状态
class ResumeStatusRequest(BaseModel):
    status:int

#关联状态的请求体
class ResumeBindStatusRequest(BaseModel):
    position_id:int=Field(alias="positionId")


class ParseUploadFile(BaseModel):
    file_name:str
    content_type:Optional[str]=None
    source_type:Literal["file","zip"]
    temp_path:str

class ResumeUploadItem(BaseModel):
    file_name:str
    object_name:str
    url:str
    position_id:Optional[int]
    status:str
    message:str=""

class ResumeUploadResult(BaseModel):
    file_name:str
    status:Literal["success","failed"]
    resume_id:Optional[int]=None
    error:Optional[str]=None

class UploadResumesResponse(BaseModel):
    total:int
    success:int
    failed:int
    results:List[ResumeUploadResult]

class ResumePositionInfo(BaseModel):
    id:int
    name:str

class ResumeDetailResponse(BaseModel):
    id:int
    candidate_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    education: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    work_years: Optional[int] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    skills: Optional[List[str]] = None
    work_experience: Optional[List[WorkExperienceItem]] = None
    project_experience: Optional[List[ProjectExperienceItem]] = None
    education_experience: Optional[List[EducationExperienceItem]] = None
    resume_summary: Optional[str] = None
    position:Optional[ResumePositionInfo]=None
    status:Optional[int] = None
    status_name:Optional[str] = None
    parse_status: int | None = None
    parse_status_name: str | None = None
    created_at:Optional[datetime] = None


#简历列表
class ResumeListItemResponse(BaseModel):
    id:int
    candidate_name:str=None
    phone:Optional[str] = None
    education: Optional[str] = None
    work_years:Optional[int] = None
    current_company:Optional[str] = None
    position_id:Optional[int] = None
    status: Optional[int] = None
    status_name:Optional[str] = None
    parse_status: int | None = None
    parse_status_name: str | None = None
    created_at:Optional[datetime] = None

class ResumeListResponse(BaseModel):
    total:int
    page:int
    page_size:int
    data:List[ResumeListItemResponse]




