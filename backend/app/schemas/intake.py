from datetime import datetime

from pydantic import BaseModel, Field


class IntakeParseRequest(BaseModel):
    raw_message: str = Field(..., min_length=1)
    source_channel: str = "企业微信-招聘群"
    sender: str | None = None


class IntakeParsedResult(BaseModel):
    candidate_name: str
    position_name: str | None = None
    education: str | None = None
    work_years: int | None = None
    stage: str | None = None
    interview_time: str | None = None
    interviewer: str | None = None
    owner: str | None = None
    source_channel: str = "企业微信-招聘群"
    raw_message: str
    confidence: float = 0.5
    needs_review: bool = True


class IntakeParseResponse(IntakeParsedResult):
    message_id: int
    doc_row_id: int
    sync_status: str = "synced"


class IntakeMessageItem(IntakeParsedResult):
    id: int
    sender: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TencentDocRowItem(BaseModel):
    id: int
    message_id: int
    candidate_name: str
    position_name: str | None = None
    stage: str | None = None
    interview_time: str | None = None
    owner: str | None = None
    source_channel: str
    sync_status: str
    needs_review: bool
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class IntakeEventItem(BaseModel):
    id: int
    event_type: str
    title: str
    detail: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
