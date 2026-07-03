import json
from tkinter import dnd

from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session
from starlette import status

from api.position import get_position_by_id
from app.crud.summary import get_summary_by_id
from app.config import settings
from app.crud.resume import get_resume_by_id
from app.prompt.evaluation_generate_prompt import EVALUATION_GENERATE_PROMPT
from app.schemas.evaluations import EvaluationGenerateResponse, EvaluationLLMResult
from crud.evaluations import get_evaluation_by_summary_id
from models.evaluations import InterviewEvaluation


#这里是api层调用的，生成面试评价并封装返回结果
def generate_evaluations(id:int,db:Session):
    #1.先根据id查出构建prompt所需要的字段
    db_summary=get_summary_by_id(id,db)
    if not db_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该面试摘要不存在")
    db_resume=get_resume_by_id(db,db_summary.resume_id)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该候选人简历不存在")
    db_position=None
    db_position=get_position_by_id(db_resume.position_id,db)

    #2.构建提示词
    prompt=EVALUATION_GENERATE_PROMPT.format(
        candidate_name=db_resume.candidate_name,
        position_name=db_position.position_name,
        requirements=db_position.requirements,
        summary_overview=db_summary.summary_overview,
        key_qa_text=db_summary.key_qa,
        technical_skills=db_summary.technical_skills,
        soft_skills=db_summary.soft_skills,
        highlights=db_summary.highlights,
        concerns=db_summary.concerns
    )
    llm=ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL
    )
    structured_llm=llm.with_structured_output(EvaluationLLMResult)
    #现在llm返回的是pydantic类，就是我们定义的返回类
    llm_result =structured_llm.invoke(prompt)
    llm_result=EvaluationLLMResult.model_validate(llm_result) #现在就封装好了pydantic类

    #写入数据库
    db_evaluation=get_evaluation_by_summary_id(db_summary.id,db)
    if not db_evaluation:
        db_evaluation = InterviewEvaluation(
            resume_id=db_resume.id,
            recording_id=db_summary.recording_id,
            summary_id=db_summary.id
        )
        db.add(db_evaluation)

    #现在开始放响应的数据
    db_evaluation.professional_score=llm_result.scores.professional.score
    db_evaluation.professional_comment=llm_result.scores.professional.comment
    db_evaluation.logic_score=llm_result.scores.logic.score
    db_evaluation.logic_comment=llm_result.scores.logic.comment
    db_evaluation.communication_score=llm_result.scores.communication.score
    db_evaluation.communication_comment=llm_result.scores.communication.comment
    db_evaluation.learning_score=llm_result.scores.learning.score
    db_evaluation.learning_comment=llm_result.scores.learning.comment
    db_evaluation.teamwork_score=llm_result.scores.teamwork.score
    db_evaluation.teamwork_comment=llm_result.scores.teamwork.comment
    db_evaluation.culture_score=llm_result.scores.culture_fit.score
    db_evaluation.culture_comment=llm_result.scores.culture_fit.comment

    db_evaluation.total_score = llm_result.total_score
    db_evaluation.recommendation = llm_result.recommendation
    db_evaluation.ai_comment = llm_result.ai_comment
    db_evaluation.key_strengths = llm_result.key_strengths
    db_evaluation.improvement_areas = llm_result.improvement_areas
    db_evaluation.hiring_suggestion = llm_result.hiring_suggestion

    db.flush()
    db.commit()
    db.refresh(db_evaluation)

    #开始封装返回类
    result= EvaluationGenerateResponse(
        id=db_evaluation.id,
        resume_id=db_resume.id,
        scores=llm_result.scores,
        total_score=llm_result.total_score,
        recommendation=llm_result.recommendation,
        ai_comment=llm_result.ai_comment,
        key_strengths=llm_result.key_strengths,
        improvement_areas=llm_result.improvement_areas,
        hiring_suggestion=llm_result.hiring_suggestion

    )
    return result