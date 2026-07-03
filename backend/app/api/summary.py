from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.testing.config import db_url
from starlette import status
import json
from app.crud.summary import get_summary_by_recording_id,update_summary,get_recording_by_summary_id
from database import get_db
from app.schemas.summary import SummaryGenerateRequest
from app.schemas.summary import SummaryGenerateResponse, SummaryKeyQAItem, UpdateSummaryRequest
from app.services.summary import generate_summary
from app.utils.response import success_response

router=APIRouter(prefix="/api/v1/summaries",tags=["面试摘要提取模块"])

@router.post("/generate",summary="生成摘要")
def generate_interview_summary(data:SummaryGenerateRequest,db:Session=Depends(get_db)):
    result=generate_summary(data.recording_id,db)
    return success_response(message="生成面试摘要成功",data=result)

@router.get("/{recording_id}",summary="获取摘要")
def get_interview_summary(recording_id:int,db:Session=Depends(get_db)):
    db_summary =get_summary_by_recording_id(recording_id,db)
    if not db_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该录音还未生成摘要")
    data=SummaryGenerateResponse(
        id=db_summary.id,
        recording_id=db_summary.recording_id,
        resume_id=db_summary.resume_id,
        summary_overview= db_summary.summary_overview,
        #需要特别处理的是key_qa，因为其中是含有多个qa的
        key_qa= [SummaryKeyQAItem(**item) #这里是将item的json解包成dict对应放入Summary中
                 for item in
                 #下面是将keyqa json.loads将json格式的字符串转化为python对象
                 (json.loads(db_summary.key_qa) if db_summary.key_qa else [])],
        #需要的是list对象，就都需要json.loads转化为python对象再放入，上面需要遍历是因为有一样的，有几个list，下面就一个list，就不用遍历
        technical_skills=json.loads(db_summary.technical_skills) if db_summary.technical_skills else [],
        soft_skills=json.loads(db_summary.soft_skills) if db_summary.soft_skills else [],
        highlights=json.loads(db_summary.highlights) if db_summary.highlights else [],
        concerns=json.loads(db_summary.concerns) if db_summary.concerns else [],
        candidate_questions=json.loads(db_summary.candidate_questions) if db_summary.candidate_questions else []
    )

    return success_response(message="获取摘要成功",data=data)

@router.put("/{id}",summary="更新摘要")
def update_interview_summary(id:int,data:UpdateSummaryRequest,db:Session=Depends(get_db)):
    db_summary=update_summary(id,data,db)
    if not db_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该摘要不存在")
    db.commit()
    db.refresh(db_summary)
    #组装返回的格式
    result = SummaryGenerateResponse(
        id=db_summary.id,
        recording_id=db_summary.recording_id,
        resume_id=db_summary.resume_id,
        summary_overview=db_summary.summary_overview,
        # 需要特别处理的是key_qa，因为其中是含有多个qa的
        key_qa=[SummaryKeyQAItem(**item)  # 这里是将item的json解包成dict对应放入Summary中
                for item in
                # 下面是将keyqa json.loads将json格式的字符串转化为python对象
                (json.loads(db_summary.key_qa) if db_summary.key_qa else [])],
        # 需要的是list对象，就都需要json.loads转化为python对象再放入，上面需要遍历是因为有一样的，有几个list，下面就一个list，就不用遍历
        technical_skills=json.loads(db_summary.technical_skills) if db_summary.technical_skills else [],
        soft_skills=json.loads(db_summary.soft_skills) if db_summary.soft_skills else [],
        highlights=json.loads(db_summary.highlights) if db_summary.highlights else [],
        concerns=json.loads(db_summary.concerns) if db_summary.concerns else [],
        candidate_questions=json.loads(db_summary.candidate_questions) if db_summary.candidate_questions else []
    )

    return success_response(message="更新摘要成功", data=result)

#重新生成摘要其实就是再次调用一下第一个方法
@router.post("/{id}/regenerate",summary="重新生成摘要")
def regenerate_summary(id:int,db:Session=Depends(get_db)):
    db_recording_id=get_recording_by_summary_id(id,db)
    if not db_recording_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该摘要对应的录音不存在")
    result=generate_summary(db_recording_id,db)
    return success_response(message="重新生成摘要成功",data=result)

