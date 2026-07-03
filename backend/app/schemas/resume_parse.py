#定义解析得到的结构化结果
from typing import Optional, List

from pydantic import BaseModel


class WorkExperienceItem(BaseModel):
    company:Optional[str]=None
    position:Optional[str]=None
    start_date:Optional[str]=None
    end_date:Optional[str]=None
    description:Optional[str]=None

class ProjectExperienceItem(BaseModel):
    project_name:Optional[str]=None
    role:Optional[str]=None
    description:Optional[str]=None

class EducationExperienceItem(BaseModel):
    school:Optional[str]=None
    major:Optional[str]=None
    degree:Optional[str]=None
    start_date:Optional[str]=None
    end_date:Optional[str]=None

class ResumeParseResult(BaseModel):
    candidate_name:Optional[str]=None
    phone:Optional[str]=None
    email:Optional[str]=None
    education:Optional[str]=None
    school:Optional[str]=None
    major:Optional[str]=None
    work_years:Optional[int]=None
    current_company:Optional[str]=None
    current_position:Optional[str]=None
    skills:Optional[List[str]]=None
    work_experience:Optional[List[WorkExperienceItem]]=None
    project_experience:Optional[List[ProjectExperienceItem]]=None
    education_experience:Optional[List[EducationExperienceItem]]=None
    resume_summary:Optional[str]=None
