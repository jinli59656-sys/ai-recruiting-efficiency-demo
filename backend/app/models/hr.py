
from sqlalchemy import Column, BigInteger, String, Integer, func, DateTime

from app.database import Base


class SysUser(Base):
    __tablename__ = "sys_user"

    id=Column(BigInteger,primary_key=True,autoincrement=True,comment="主键ID")
    username=Column(String(50),nullable=False,comment="用户名")
    password=Column(String(100),nullable=False,comment="密码")
    real_name=Column(String(50),nullable=True,comment="真实姓名")
    email=Column(String(100),nullable=True,comment="邮箱")
    phone=Column(String(20),nullable=True,comment="手机号")
    avatar=Column(String(500),nullable=True,comment="头像url")
    status=Column(Integer,default=1,nullable=False,comment="状态")
    last_login_time=Column(DateTime,server_default=func.now(),onupdate=func.now(),comment="最后登录时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")