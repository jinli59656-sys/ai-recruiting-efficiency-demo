

from sqlalchemy import Index, Column, BigInteger, Integer, DateTime,func,String

from app.database import Base


class InterviewQuestion(Base):
    __tablename__ = "interview_question"

    __table_args__ = (
        Index("idx_difficulty","difficulty"),
        Index("idx_position","position_id"),
        Index("idx_resume","resume_id"),
        Index("idx_type","question_type")
    )

    id=Column(BigInteger,primary_key=True,autoincrement=True,comment="主键ID")
    position_id=Column(BigInteger,nullable=True,comment="关联岗位ID")
    resume_id=Column(BigInteger,nullable=True,comment="关联简历ID")
    question_type=Column(String(20),nullable=False,comment="题目类型：technical/bahavioral/situational/open")
    difficulty=Column(String(10),nullable=False,comment="难度：junior/middle/senior")
    question_content=Column(String,nullable=False,comment="题目内容")
    reference_answer=Column(String,nullable=True,comment="参考答案")
    scoring_points=Column(String,nullable=True,comment="评分要点")
    source=Column(String(50),nullable=True,comment="题目来源")
    is_saved=Column(Integer,default=0,nullable=True,comment="是否保存到题库")
    created_at=Column(DateTime,default=func.now(),nullable=False,comment="创建时间")
