#创建的是前端传入的请求体和我们返回给前端的信息
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

#这个是前端传入的数据 --创建position
class PositionCreate(BaseModel):
    position_name:str=Field(...,max_length=100,description="岗位名称")
    department:str=Field(...,max_length=100,description="所属部门")
    job_description:str=Field(...,description="岗位职责")
    requirements:str=Field(...,description="任职要求")
    salary_range:Optional[str]=Field(None,max_length=50,description="薪资范围") #这个因为在设计数据库表的时候就有说非必填
    work_location:Optional[str]=Field(None,max_length=100,description="工作地点")
    headcount:int=Field(default=1,ge=1,description="招聘人数")
    status:int=Field(default=1,ge=1,le=3,description="状态")

#前端传入 -- 更新岗位 -- 这里的None不是改为None，而是默认None不更改
class PositionUpdate(BaseModel):
    position_name:Optional[str]=Field(None,max_length=100)
    department:Optional[str]=Field(None,max_length=100)
    job_description:Optional[str]=None #没有限制，可以选填 ，默认为None
    requirements:Optional[str]=None
    salary_range:Optional[str]=None
    work_location:Optional[str]=None
    headcount:Optional[int]=Field(None,ge=1)
    status:Optional[int]=Field(None,ge=1,le=3)

#前端传入更新状态
class PositionStatusUpdate(BaseModel):
    status:int=Field(...,ge=1,le=3,description="状态 ：1开放，2暂停，3关闭")


#后端响应 ---岗位响应
class PositionResponse(BaseModel):
    id:int
    position_name:str
    department:str
    job_description:str
    requirements:str
    salary_range:Optional[str]
    work_location:Optional[str]
    headcount:int
    status:int
    status_name:str=""
    created_at:datetime
    updated_at:datetime

    #允许接口响应模型直接接收数据库 ORM 对象。
    class Config:
        from_attributes=True  #也可以从属性中取值，可能对象不是dict模式的，而是ORM，所以仅仅是dict取值是不行的

    def __init__(self,**data):
        #先将类的字段有的都填入
        super().__init__(**data)
        #状态状态映射
        status_map={1:"开放招聘",2:"暂停招聘",3:"已关闭"}
        #根据status，得到status_name
        self.status_name=status_map.get(self.status,"未知")

#后端返回 -- 分页响应
class PositionListResponse(BaseModel):
    total:int
    items:list[PositionResponse]
    page:int
    page_size:int