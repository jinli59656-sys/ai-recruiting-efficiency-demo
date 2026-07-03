from sqlalchemy import Column, BigInteger, String, Integer, DateTime, func, Index, ForeignKey, Date, Text

from app.database import Base


class InterviewRecording(Base):

    __tablename__ = "interview_recording"

    __table_args__ = (
        Index("idx_interview_date","interview_date"),
        Index("idx_resume","resume_id"),
        Index("idx_status","transcript_status")
    )


    id=Column(BigInteger,autoincrement=True,primary_key=True,comment="主键ID")
    resume_id=Column(BigInteger,ForeignKey("resume.id"),nullable=False,comment="关联简历ID")
    position_id=Column(BigInteger,ForeignKey("job_position.id"),nullable=True,comment="关联岗位ID")
    file_name=Column(String(200),nullable=False,comment="文件名")
    file_path=Column(String(500),nullable=False,comment="存储路径")
    file_type=Column(String(10),nullable=False,comment="文件类型：mp3/wav/m4a")
    file_size=Column(BigInteger,nullable=False,comment="文件大小")
    duration=Column(Integer,nullable=True,comment="时长")
    transcript=Column(String,nullable=True,comment="文字稿")
    transcript_json=Column(Text,nullable=True,comment="文字稿的结构化转写结果")
    transcript_status=Column(Integer,default=0,nullable=False,comment="转写状态：0-未转写  1-转写中  2-已完成  3-失败")
    transcript_error=Column(String(500),nullable=True,comment="转写错误信息")
    interviewer=Column(String(50),nullable=True,comment="面试官")
    interview_date=Column(Date,nullable=True,comment="面试日期")
    created_at=Column(DateTime,default=func.now(),nullable=False,comment="创建时间")
    updated_at=Column(DateTime,default=func.now(),onupdate=func.now(),nullable=False,comment="更新时间")
