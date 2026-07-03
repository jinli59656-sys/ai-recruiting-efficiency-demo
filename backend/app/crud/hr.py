from sqlalchemy.orm import Session

from app.models.hr import SysUser
from app.utils import security
from schemas.hr import UserRequest


#验证用户名和密码
def authenticate_hr(hr_name:str,password:str,db:Session):
    db_hr=db.query(SysUser).filter(SysUser.username==hr_name).first()
    if not db_hr:
        return None
    if not security.verify_password(password, db_hr.password):
        return None
    return db_hr

def get_user_by_username(db:Session,username):
    db_user =db.query(SysUser).filter(SysUser.username==username).first()
    return db_user

def create_user(db:Session,data:UserRequest):
    # 需要先对密码进行加密处理
    # 加密抽取放在工具
    hashed_password = security.get_hash_password(data.password)
    user = SysUser(username=data.username, password=hashed_password,status=1)
    db.add(user)  # 这里不用加await是因为await的等待是为了接收返回的值，这里add不返回值
    db.commit()
    db.refresh(user)  # 这里是确认一下user是否是最新的值，有返回，用await
    return user

