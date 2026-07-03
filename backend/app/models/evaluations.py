from sqlalchemy import Index, Column, BigInteger, Integer, String, DECIMAL, Text, JSON, DateTime, func

from database import Base


class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluation"

    __table_args__ = (
        Index("idx_resume", "resume_id"),
        Index("idx_score", "total_score"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")

    resume_id = Column(BigInteger, nullable=False, comment="关联简历ID")
    recording_id = Column(BigInteger, nullable=True, comment="关联录音ID")
    summary_id = Column(BigInteger, nullable=True, comment="关联摘要ID")

    professional_score = Column(Integer, nullable=False, comment="专业能力")
    professional_comment = Column(String(200), nullable=True, comment="专业能力评价")

    logic_score = Column(Integer, nullable=False, comment="逻辑思维")
    logic_comment = Column(String(200), nullable=True, comment="逻辑思维评价")

    communication_score = Column(Integer, nullable=False, comment="沟通表达")
    communication_comment = Column(String(200), nullable=True, comment="沟通表达评价")

    learning_score = Column(Integer, nullable=False, comment="学习能力")
    learning_comment = Column(String(200), nullable=True, comment="学习能力评价")

    teamwork_score = Column(Integer, nullable=False, comment="团队协作")
    teamwork_comment = Column(String(200), nullable=True, comment="团队协作评价")

    culture_score = Column(Integer, nullable=False, comment="文化匹配")
    culture_comment = Column(String(200), nullable=True, comment="文化匹配评价")

    total_score = Column(DECIMAL(5, 2), nullable=False, comment="综合得分")
    recommendation = Column(String(20), nullable=False, comment="推荐等级")

    ai_comment = Column(Text, nullable=True, comment="AI评语")
    key_strengths = Column(JSON, nullable=True, comment="核心优势")
    improvement_areas = Column(JSON, nullable=True, comment="待提升")
    hiring_suggestion = Column(Text, nullable=True, comment="录用建议")
    hr_comment = Column(Text, nullable=True, comment="HR评价")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )