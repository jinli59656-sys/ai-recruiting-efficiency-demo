from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.database import get_db
from app.schemas.evaluations import (EvaluationGenerateRequest,EvaluationGenerateResponse,
                                     EvaluationScores,EvaluationScoreItem,AddHrCommentRequest,
                                     AddHrCommentResponse,EvaluationHistoryItem)
from app.services.evaluations import generate_evaluations
from app.utils.response import success_response
from app.crud.evaluations import get_evaluation_by_resume_id,add_evaluation_hr_comment,get_evaluation_by_id
from crud.evaluations import get_evaluations_by_resume_id

router=APIRouter(prefix="/api/v1/evaluations",tags=["面试评价模块"])

@router.post("/generate",summary="生成评价")
def generate_interview_evaluations(data:EvaluationGenerateRequest,db:Session=Depends(get_db)):
    result=generate_evaluations(data.summary_id,db)

    return success_response(message="生成面试评价成功",data=result)

@router.get("/{id}",summary="获取评价")
def get_evaluation(id:int,db:Session=Depends(get_db)):
    db_evaluation=get_evaluation_by_id(id,db)
    if not db_evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该面试评价不存在")

    data = EvaluationGenerateResponse(
        id=db_evaluation.id,
        resume_id=db_evaluation.resume_id,
        scores=EvaluationScores(
            professional=EvaluationScoreItem(
                score=db_evaluation.professional_score,
                comment=db_evaluation.professional_comment
            ),
            logic=EvaluationScoreItem(
                score=db_evaluation.logic_score,
                comment=db_evaluation.logic_comment
            ),
            communication=EvaluationScoreItem(
                score=db_evaluation.communication_score,
                comment=db_evaluation.communication_comment
            ),
            learning=EvaluationScoreItem(
                score=db_evaluation.learning_score,
                comment=db_evaluation.learning_comment
            ),
            teamwork=EvaluationScoreItem(
                score=db_evaluation.teamwork_score,
                comment=db_evaluation.teamwork_comment
            ),
            culture_fit=EvaluationScoreItem(
                score=db_evaluation.culture_score,
                comment=db_evaluation.culture_comment
            ),
        ),
        total_score=float(db_evaluation.total_score),
        recommendation=db_evaluation.recommendation,
        ai_comment=db_evaluation.ai_comment,
        key_strengths=db_evaluation.key_strengths or [],
        improvement_areas=db_evaluation.improvement_areas or [],
        hiring_suggestion=db_evaluation.hiring_suggestion
    )

    return success_response(message="获取面试评价成功",data=data)

@router.put("/{id}/hr-comment",summary="HR补充评价")
def add_hr_comment(id:int,data:AddHrCommentRequest,db:Session=Depends(get_db)):
    db_evaluation=add_evaluation_hr_comment(id,data.hr_comment,db)
    if not db_evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="没有面试评价")
    db.commit()
    db.refresh(db_evaluation)
    result=AddHrCommentResponse(hr_comment=db_evaluation.hr_comment)
    return success_response(message="HR补充评价成功",data=result)

@router.get("/history/{resume_id}",summary="获取评价历史")
def get_evaluation_history(resume_id:int,db:Session=Depends(get_db)):
    total,db_evaluations=get_evaluations_by_resume_id(resume_id,db)
    if not db_evaluations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="没有该候选人的评价")
    results=[]
    for db_evaluation in db_evaluations:
        result = EvaluationHistoryItem(
            id=db_evaluation.id,
            resume_id=db_evaluation.resume_id,
            total_score=db_evaluation.total_score,
            recommendation=db_evaluation.recommendation,
            created_at=db_evaluation.created_at
        )
        results.append(result)

    return success_response(message="获取面试评价历史记录成功",data=results)


