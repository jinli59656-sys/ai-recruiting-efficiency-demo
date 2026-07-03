from sqlalchemy import Column, BigInteger, String, Integer, Text, SmallInteger, DateTime, func
from sqlalchemy.dialects.mssql import JSON

from app.database import Base


class Resume(Base):
    __tablename__ = "resume"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    candidate_name = Column(String(50), nullable=False, comment="候选人姓名")
    phone = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    education = Column(String(20), nullable=True, comment="学历")
    school = Column(String(100), nullable=True, comment="毕业院校")
    major = Column(String(100), nullable=True, comment="专业")
    work_years = Column(Integer, nullable=True, comment="工作年限")
    current_company = Column(String(100), nullable=True, comment="当前公司")
    current_position = Column(String(100), nullable=True, comment="当前职位")
    skills = Column(JSON, nullable=True, comment="技能标签")
    work_experience = Column(JSON, nullable=True, comment="工作经历")
    project_experience = Column(JSON, nullable=True, comment="项目经验")
    education_experience = Column(JSON, nullable=True, comment="教育经历")
    resume_summary = Column(Text, nullable=True, comment="AI简历摘要")
    original_content = Column(Text, nullable=True, comment="简历原始文本")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_name = Column(String(200), nullable=False, comment="原始文件名")
    file_type = Column(String(10), nullable=False, comment="文件类型")
    file_size = Column(BigInteger, nullable=True, comment="文件大小(字节)")
    milvus_id = Column(String(100), nullable=True, comment="Milvus向量ID")
    position_id = Column(BigInteger, nullable=True, comment="关联岗位ID")
    status = Column(SmallInteger, nullable=False, default=1, comment="状态")
    parse_status = Column(SmallInteger, nullable=False, default=0, comment="解析状态")
    is_deleted = Column(SmallInteger, nullable=False, default=0, comment="软删除")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")



