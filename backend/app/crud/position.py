from typing import Optional

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from starlette import status

from app.models import JobPosition
from app.schemas.position import PositionUpdate


#创建岗位
def create_position(
        position_name:str,
        department:str,
        job_description:str,
        requirements:str,
        salary_range:str,
        work_location:str,
        headcount:int,
        db:Session
):
    position =JobPosition(position_name=position_name,department=department,job_description=job_description,
                          requirements=requirements,salary_range=salary_range,work_location=work_location,
                          headcount=headcount)
    db.add(position)
    db.flush()
    query=db.query(JobPosition).filter(JobPosition.position_name==position_name).first()

    return query

#得到岗位列表
def get_position_list(
        db:Session,
        page:int =1,
        page_size=10,
        position_name:Optional[str]=None,
        department:Optional[str]=None,
        status:Optional[int]=None
):

    #先得到正常状态的
    query=db.query(JobPosition).filter(JobPosition.is_deleted==0)
    #筛选条件：
    if position_name:
        #如果有名字，就继续过滤，根据名字模糊匹配
        query=query.filter(JobPosition.position_name.like(f"%{position_name}%"))
    if department:
        query=query.filter(JobPosition.department==department) #有部门就筛选部门
    if status:
        query=query.filter(JobPosition.status==status)

    #现在得到了筛选后的全部结果
    #总数
    total=query.count()

    #分页
    items=(query.order_by(JobPosition.created_at.desc())
           .offset((page-1)*page_size)
           .limit(page_size).all())
    return total,items

#根据id获取岗位，获取岗位详情
def get_position_by_id(position_id:int,db:Session):
    query=db.query(JobPosition).filter(JobPosition.id==position_id,JobPosition.is_deleted==0)
    return query.first()

#更新岗位信息 根据id更新
def update_position(position_id:int,data:PositionUpdate,db:Session):
    #先根据id获取下当前用户
    db_position=get_position_by_id(position_id,db)
    if db_position:
        user_data=data.model_dump(exclude_unset=True)
        for key,value in user_data.items():
            setattr(db_position,key,value)
    return db_position

#删除岗位
def delete_position(position_id:int,db:Session):
    #这里的删除采取的是软删除，就是改一下is_deleted的状态
    db_position=get_position_by_id(position_id,db)
    if db_position:
        db_position.is_deleted=1
    return db_position

#更新岗位的状态
def update_status(position_id:int,status:int,db:Session):
    db_position=get_position_by_id(position_id,db)
    if db_position:
        db_position.status=status
    return db_position

