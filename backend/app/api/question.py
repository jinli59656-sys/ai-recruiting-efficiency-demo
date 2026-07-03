import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from app.crud import question
from app.crud.position import get_position_by_id
from app.crud.resume import get_resume_by_id
from app.database import get_db
from app.schemas.question import QuestionCreateRequest, QuestionListInfo, QuestionListResponse, QuestionUpdateRequest, \
    QuestionItemResponse, QuestionSaveRequest
from app.services.question import generate_questions_and_save
from app.utils.response import success_response

router=APIRouter(prefix="/api/v1/questions",tags=["面试题生成模块"])

@router.post("/generate",summary="生成面试题")
def generate_questions(data:QuestionCreateRequest,db:Session=Depends(get_db)):
    # 1.先根据传进来的参数，查询position和resume
    db_position=None
    db_resume=None
    if data.position_id is not None:
        db_position=get_position_by_id(data.position_id,db)
        if not db_position:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该岗位不存在")

    if data.resume_id is not None:
        db_resume=get_resume_by_id(db,data.resume_id)
        if not db_resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该简历不存在")

    result=generate_questions_and_save(data=data,db_position=db_position,db_resume=db_resume,db=db)

    return success_response(message="生成面试题成功",data=result)

#获取题目列表
@router.get("",summary="获取题目列表")
def get_question_list(page:int=Query(default=1,ge=1,description="页码"),
                      page_size:int=Query(default=10,le=50,description="每页数量")
                      ,db:Session=Depends(get_db)):
    total,items=question.get_question_list(page,page_size,db)
    data= QuestionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[
      QuestionListInfo(
          id=item.id,
          position_id=item.position_id,
          resume_id=item.resume_id,
          question_type=item.question_type,
          difficulty=item.difficulty,
          question_content=item.question_content,
          reference_answer=item.reference_answer,
          scoring_points=json.loads(item.scoring_points) if item.scoring_points else [],
          source=item.source,
          is_saved=item.is_saved
      )
      for item in items
  ]
    )
    return success_response(message="获取题目列表成功",data=data)

#编辑题目
@router.put("/{id}",summary="编辑题目")
def update_question(id:int,data:QuestionUpdateRequest,db:Session=Depends(get_db)):
    db_question=question.update_question(id,data,db)
    db.commit()
    db.refresh(db_question)
    data=QuestionItemResponse(
        id=id,
        type=db_question.question_type,
        difficulty=db_question.difficulty,
        question=db_question.question_content,
        reference_answer=db_question.reference_answer,
        scoring_points=json.loads(db_question.scoring_points),
        source=db_question.source,
        is_saved=db_question.is_saved
    )

    return success_response(message="编辑题目成功",data=data)

@router.delete("/{id}",summary="删除题目")
def delete_question(id:int,db:Session=Depends(get_db)):
    db_question=question.delete_question(id,db)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该题目不存在")
    db.flush()
    db.commit()
    return success_response(message="删除题目成功")

#保存题目到题库，就是修改数据库的is_saved字段
@router.post("/save-to-bank",summary="保存到题库")
def save_question(ids:QuestionSaveRequest,db:Session=Depends(get_db)):
    count=question.save_batch(ids.ids,db)
    db.flush()
    db.commit()
    return success_response(message=f"成功保存了{count}条题目")


