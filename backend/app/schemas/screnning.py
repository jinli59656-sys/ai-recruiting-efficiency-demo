from typing import Optional, List

from pydantic import Field, BaseModel

from app.schemas.resume import ResumePositionInfo


class PositionMatchRequest(BaseModel):
    position_id:int=Field(alias="positionId")
    top_n:Optional[int]=Field(default=10,alias="topN",ge=1,le=50)
    min_education:Optional[str]=Field(None,alias="minEducation")
    min_work_years:Optional[int]=Field(None,alias="minWorkYears",ge=0)
    required_skills:Optional[list]=Field(None,alias="requiredSkills")

#自定义筛选
class CustomMatchRequest(BaseModel):
    query:str
    top_n:int=Field(default=10,alias="topN",ge=1,le=50)

class BatchMarkRequest(BaseModel):
    resume_ids:List[int]
    mark:int


class PositionMatchAnalysis(BaseModel):
    match_advantages:List[str]
    match_weaknesses:List[str]
    overall_comment:str
    interview_suggestions:List[str]

class PositionMatchInfo(BaseModel):
    resume_id: int
    candidate_name: str
    education:str
    work_years:int
    current_position:str
    match_score:int
    similarity: float
    recommendation: str
    match_analysis: PositionMatchAnalysis |None=None #这里先不返回真的，不然等待时间太长

class PositionAnalysisResponse(BaseModel):
    position_id:int
    resume_id:int
    similarity:float
    result:PositionMatchAnalysis


class PositionMatchResponse(BaseModel):
    position:Optional[ResumePositionInfo]
    total_matched:int
    results:List[PositionMatchInfo]

class CustomMatchResponse(BaseModel):
    query:str
    total_matched:int
    results:List[PositionMatchInfo]


