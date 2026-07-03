from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, Integer, String, Text, func

from database import Base


class RecruitmentMessage(Base):
    __tablename__ = "recruitment_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    raw_message = Column(Text, nullable=False)
    source_channel = Column(String(100), nullable=False, default="企业微信-招聘群")
    sender = Column(String(50), nullable=True)
    candidate_name = Column(String(50), nullable=False)
    position_name = Column(String(100), nullable=True)
    education = Column(String(20), nullable=True)
    work_years = Column(Integer, nullable=True)
    stage = Column(String(50), nullable=True)
    interview_time = Column(String(100), nullable=True)
    interviewer = Column(String(50), nullable=True)
    owner = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=False, default=0.5)
    needs_review = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class RecruitmentDocRow(Base):
    __tablename__ = "recruitment_doc_rows"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, nullable=False)
    candidate_name = Column(String(50), nullable=False)
    position_name = Column(String(100), nullable=True)
    stage = Column(String(50), nullable=True)
    interview_time = Column(String(100), nullable=True)
    owner = Column(String(50), nullable=True)
    source_channel = Column(String(100), nullable=False)
    sync_status = Column(String(20), nullable=False, default="synced")
    needs_review = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class RecruitmentSyncEvent(Base):
    __tablename__ = "recruitment_sync_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, nullable=True)
    doc_row_id = Column(BigInteger, nullable=True)
    event_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
