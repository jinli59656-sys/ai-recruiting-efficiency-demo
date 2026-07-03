from datetime import datetime

from pydantic import BaseModel, Field


class CreateCompareRequest(BaseModel):
    position_id:int=Field(...,alias="positionId")
    resume_ids:list[int]=Field(...,alias="resumeIds")


class PositionItem(BaseModel):
    id:int
    name:str


class EvaluationItem(BaseModel):
    professional_score:float
    logic_score:float
    communication_score:float
    learning_score:float
    teamwork_score:float
    culture_score:float
    total_score:float


class CandidateItem(BaseModel):
    resume_id:int
    name:str
    education:str |None
    school:str | None
    work_years:int | None=None
    current_position:str |None
    skills:list[str] | None
    evaluation:EvaluationItem


#响应
class CreateCompareResponse(BaseModel):
    id:int
    position:PositionItem
    candidates:list[CandidateItem]

class CandidateAnalysisItem(BaseModel):
    name:str
    advantages_over_others:list[str]
    disadvantages:list[str]
    suitable_scenarios:str
    risk_points:str

class ComparisonRankingItem(BaseModel):
    rank:int
    name:str
    score:float
    reason:str

class ComparisonRecommendation(BaseModel):
    best_choice:str
    reason:str
    alternative:str
    alternative_reason:str

class ComparisonAnalysisLLMResult(BaseModel):
    comparison_summary:str
    candidate_analysis:list[CandidateAnalysisItem]
    ranking:list[ComparisonRankingItem]
    recommendation:ComparisonRecommendation
    hiring_advice:str

class ComparisonAnalysisResponse(BaseModel):
    id:int
    comparison_summary:str
    candidate_analysis:list[CandidateAnalysisItem]
    ranking:list[ComparisonRankingItem]
    recommendation:ComparisonRecommendation
    hiring_advice:str


class ComparisonHistoryItem(BaseModel):
    id:int
    position:PositionItem
    resume_ids:list[int]
    candidate_count:int
    has_ai_analysis:bool
    has_ranking:bool

    top_ranked_candidate:str |None=None
    top_ranked_score:float |None=None

    best_choice:str |None=None
    best_choice_reason:str|None=None

    created_at:datetime

class ComparisonListResponse(BaseModel):
    total:int
    page:int
    page_size:int
    items:list[ComparisonHistoryItem]


class ComparisonDetailResponse(BaseModel):
    id: int
    position: PositionItem
    candidates: list[CandidateItem]
    ai_analysis: dict | None = None
    ranking: list[ComparisonRankingItem] | None = None
    created_at: datetime