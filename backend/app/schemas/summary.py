from typing import Optional

from pydantic import BaseModel, Field


class SummaryGenerateRequest(BaseModel):
    recording_id:int=Field(...,alias="recordingId")



class SummaryKeyQAItem(BaseModel):
    question:str
    answer_summary:str
    answer_quality:str

#更新摘要
class UpdateSummaryRequest(BaseModel):
    summary_overview:Optional[str]=Field(default=None,alias="summaryOverview")
    key_qa:Optional[list[SummaryKeyQAItem]]=Field(default=None,alias="keyQa")
    technical_skills:Optional[list[str]]=Field(default=None,alias="technicalSkills")
    soft_skills:Optional[list[str]]=Field(default=None,alias="softSkills")
    highlights:Optional[list[str]]=Field(default=None)
    concerns:Optional[list[str]]=Field(default=None)
    candidate_questions:Optional[list[str]]=Field(default=None)


class ChunkSummaryResult(BaseModel):
    chunk_overview:str
    key_qa:list[SummaryKeyQAItem]
    technical_skills: list[str]
    soft_skills: list[str]
    highlights: list[str]
    concerns: list[str]
    candidate_questions: list[str]

#模型结构化输出
class InterviewSummaryLLMResult(BaseModel):
    summary_overview:str
    key_qa:list[SummaryKeyQAItem]
    technical_skills:list[str]
    soft_skills:list[str]
    highlights:list[str]
    concerns:list[str]
    candidate_questions:list[str]

#响应参数
class SummaryGenerateResponse(BaseModel):
    id:int
    recording_id:int
    resume_id:int
    summary_overview:str
    key_qa:list[SummaryKeyQAItem]
    technical_skills: list[str]
    soft_skills: list[str]
    highlights: list[str]
    concerns: list[str]
    candidate_questions: list[str]