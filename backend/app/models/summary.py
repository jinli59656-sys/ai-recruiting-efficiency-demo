from sqlalchemy import BigInteger, Column, ForeignKey, Text, String, DateTime, func, Index

from app.database import Base


class InterviewSummary(Base):

    __tablename__ = "interview_summary"

    __table_args__ = (
        Index("idx_resume","resume_id"),
    )

    id = Column(BigInteger, autoincrement=True, primary_key=True, comment="主键ID")
    recording_id = Column(BigInteger, ForeignKey("interview_recording.id"), nullable=False, comment="关联录音ID")
    resume_id = Column(BigInteger, ForeignKey("resume.id"), nullable=False, comment="关联简历ID")
    summary_overview = Column(Text, nullable=False, comment="面试摘要")
    key_qa = Column(String, default=None,nullable=True, comment="核心问答")
    technical_skills = Column(String, default=None,nullable=True, comment="技术能力标签")
    soft_skills = Column(String, default=None,nullable=True, comment="软技能标签")
    highlights = Column(Text, default=None,nullable=True, comment="亮点")
    concerns = Column(Text, default=None,nullable=True, comment="疑虑点")
    candidate_questions = Column(Text,default=None, nullable=True, comment="候选人提问")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")