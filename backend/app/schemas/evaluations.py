from datetime import datetime

from pydantic import BaseModel


class EvaluationGenerateRequest(BaseModel):
    summary_id:int


class EvaluationScoreItem(BaseModel):
    score: float
    comment: str | None = None


class EvaluationScores(BaseModel):
    professional: EvaluationScoreItem
    logic: EvaluationScoreItem
    communication: EvaluationScoreItem
    learning: EvaluationScoreItem
    teamwork: EvaluationScoreItem
    culture_fit: EvaluationScoreItem

class AddHrCommentRequest(BaseModel):
    hr_comment:str

class AddHrCommentResponse(BaseModel):
    hr_comment:str

class EvaluationGenerateResponse(BaseModel):
    id:int
    resume_id:int
    scores:EvaluationScores
    total_score:float
    recommendation:str
    ai_comment:str
    key_strengths:list[str]
    improvement_areas:list[str]
    hiring_suggestion:str

class EvaluationLLMResult(BaseModel):
    scores: EvaluationScores
    total_score: float
    recommendation: str
    ai_comment: str
    key_strengths: list[str]
    improvement_areas: list[str]
    hiring_suggestion: str


class EvaluationHistoryItem(BaseModel):
    id: int
    resume_id: int
    total_score: float
    recommendation: str
    created_at: datetime

class EvaluationHistoryResponse(BaseModel):
    total:int
    evaluation:list[EvaluationHistoryItem]