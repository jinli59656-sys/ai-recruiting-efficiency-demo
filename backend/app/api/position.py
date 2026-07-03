from typing import Optional

from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Session
from starlette import status

from app.crud import position
from app.database import get_db
from app.schemas.position import PositionListResponse, PositionResponse, PositionCreate, PositionUpdate, \
    PositionStatusUpdate
from app.utils.response import success_response

router=APIRouter(prefix="/api/v1/positions",tags=["岗位管理"])

#创建岗位
@router.post("",response_model=PositionResponse,summary="创建岗位")
def create_position(
        data:PositionCreate,
        db:Session=Depends(get_db)
):
    item =position.create_position(data.position_name,data.department,data.job_description,
                             data.requirements,data.salary_range,data.work_location,data.headcount
                             ,db)
    result=PositionResponse.model_validate(item)
    db.commit()
    # return result
    return success_response(message="创建岗位成功",data=result)

#分页查询岗位列表
@router.get("",response_model=PositionListResponse,summary="获取岗位列表")
def get_position(
        page:int=Query(1,ge=1,description="页码"),
        page_size:int=Query(10,ge=1,le=100,description="每页条数"),
        position_name:Optional[str]=Query(None,description="岗位名称"),
        department:Optional[str]=Query(None,description="部门"),
        status:Optional[int]=Query(None,description="状态"),
        db:Session=Depends(get_db)
):
    total,items=position.get_position_list(db,page,page_size,position_name,department,status)

    return PositionListResponse(
        total=total,
        items=[PositionResponse.model_validate(item)for item in items],
        page=page,
        page_size=page_size
    )

#根据id获取岗位详情
@router.get("/{id}",response_model=PositionResponse,summary="获取岗位详情")
def get_position_by_id(id:int,db:Session=Depends(get_db)):
    result =position.get_position_by_id(id,db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该岗位不存在")
    return PositionResponse.model_validate(result)

#更新岗位
@router.put("/{id}",response_model=PositionResponse,summary="更新岗位信息")
def update_position(id:int,data:PositionUpdate,db:Session=Depends(get_db)):
    db_position=position.update_position(id,data,db)
    if not db_position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该岗位不存在")
    db.commit()
    db.refresh(db_position)
    return PositionResponse.model_validate(db_position)

#删除岗位
@router.delete("/{id}",summary="删除岗位")
def delete_position(id:int,db:Session=Depends(get_db)):
    db_position=position.delete_position(id,db)
    if not db_position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该岗位不存在")
    db.commit()
    return {"message":"删除成功"}

#更新岗位状态
@router.patch("/{id}/status",response_model=PositionResponse,summary="更新岗位状态")
def update_status(id:int,status:PositionStatusUpdate,db:Session=Depends(get_db)):
    db_position=position.update_status(id,status.status,db)
    if not db_position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该岗位不存在")
    db.commit()
    db.refresh(db_position)
    return PositionResponse.model_validate(db_position)


