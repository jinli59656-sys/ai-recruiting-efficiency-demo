from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.crud import hr
from app.database import get_db
from app.schemas.hr import HRRequest, UserRequest
from crud.hr import get_user_by_username, create_user
from utils.response import success_response

#做的是登录
router=APIRouter(prefix="/api/v1/hr",tags=["hr登录"])

@router.post("/login")
def login(hr_data:HRRequest,db:Session=Depends(get_db)):
    db_hr=hr.authenticate_hr(hr_data.hr_name,hr_data.password,db)
    if not db_hr:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    return {"message":"登陆成功"}

@router.post("/register")
def register(user_data:UserRequest,db:Session=Depends(get_db)):
    existing_user=get_user_by_username(db,user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user =create_user(db, user_data)
    return success_response(message="注册成功")
