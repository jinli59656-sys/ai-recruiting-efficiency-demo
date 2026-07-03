from sqlalchemy import Index, Column, BigInteger, JSON, DateTime, func

from app.database import Base


class CandidateComparison(Base):
    __tablename__ = "candidate_comparison"

    __table_args__ = (
        Index("idx_position", "position_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    position_id = Column(BigInteger, nullable=False, comment="岗位ID")
    resume_ids = Column(JSON, nullable=False, comment="简历ID列表")
    comparison_data = Column(JSON, nullable=True, comment="对比数据")
    ai_analysis = Column(JSON, nullable=True, comment="AI分析")
    ranking = Column(JSON, nullable=True, comment="排名")
    created_by = Column(BigInteger, nullable=True, comment="创建人")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")