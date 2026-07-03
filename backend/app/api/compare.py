

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status
from fastapi.responses import FileResponse

from app.schemas.compare import CreateCompareRequest, PositionItem, CreateCompareResponse, ComparisonHistoryItem, \
    ComparisonListResponse, ComparisonDetailResponse, ComparisonRankingItem
from app.crud.evaluations import get_evaluation_by_recording_id
from app.crud.position import get_position_by_id
from app.crud.recordings import get_recording_by_resume_position_id
from app.crud.resume import get_resumes_by_ids
from app.database import get_db
from app.models.compare import CandidateComparison
from app.schemas.compare import CandidateItem, EvaluationItem
from app.utils.response import success_response
from app.services.compare import ai_compare_analysis,build_compare_report_pdf
from app.crud.compare import get_compare_history, get_compare


router=APIRouter(prefix="/api/v1/comparison",tags=["候选人对比模块"])

#创建对比--将简历id输入，返回他们的信息
@router.post("/create",summary="创建对比")
def create_compare(data:CreateCompareRequest,db:Session=Depends(get_db)):
    #要根据position_id去得到录音表，从而得到面试评价分
    db_position=get_position_by_id(data.position_id,db)
    if not db_position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="岗位不存在")
    db_resumes=get_resumes_by_ids(data.resume_ids,db)
    if len(db_resumes) != len(data.resume_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="简历不存在")

    position=PositionItem(
        id=db_position.id,
        name=db_position.position_name
    )
    candidates=[]

    for db_resume in db_resumes:
        db_recording = get_recording_by_resume_position_id(db_resume.id, data.position_id, db)
        if not db_recording:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="录音不存在")
        db_evaluation=get_evaluation_by_recording_id(db_recording.id,db)
        if not db_evaluation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="面试评价不存在")
        evaluation=EvaluationItem(
            professional_score=db_evaluation.professional_score,
            logic_score=db_evaluation.logic_score,
            communication_score=db_evaluation.communication_score,
            learning_score=db_evaluation.learning_score,
            teamwork_score=db_evaluation.teamwork_score,
            culture_score=db_evaluation.culture_score,
            total_score=db_evaluation.total_score
        )
        candidate = CandidateItem(
            resume_id=db_resume.id,
            name=db_resume.candidate_name,
            education=db_resume.education,
            school=db_resume.school,
            work_years=db_resume.work_years,
            current_position=db_resume.current_position,
            skills=db_resume.skills,
            evaluation=evaluation,
        )
        candidates.append(candidate)

    db_compare=CandidateComparison(
        position_id=data.position_id,
        resume_ids=data.resume_ids,
        comparison_data={
            "position": position.model_dump(),
            "candidates": [item.model_dump() for item in candidates]
        }
    )
    db.add(db_compare)
    db.commit()
    db.refresh(db_compare)
    result=CreateCompareResponse(
        id=db_compare.id,
        position=position,
        candidates=candidates
    )
    return success_response(message="创建对比成功",data=result)

@router.post("/{id}/analyze",summary="AI对比分析")
def ai_analyze(id:int,db:Session=Depends(get_db)):
    result=ai_compare_analysis(id,db)
    return success_response(message="AI对比分析成功",data=result)

@router.get("/history",summary="对比历史")
def compare_history(
        page:int=Query(1,ge=1,description="页码"),
        page_size:int =Query(10,ge=1,le=50,description="每页数量"),
        position_id:int|None=Query(None,alias="positionId",description="岗位ID"),
        db:Session=Depends(get_db)
):
    total,db_compares=get_compare_history(
        db,page,page_size,position_id
    )
    items=[]

    for db_compare in db_compares:
        db_position=get_position_by_id(db_compare.position_id, db)

        ranking=db_compare.ranking or []
        ai_analysis=db_compare.ai_analysis or {}
        recommendation=ai_analysis.get("recommendation") or {}

        top_ranked_candidate=ranking[0].get("name") if ranking else None
        top_ranked_score=ranking[0].get("score") if ranking else None

        item=ComparisonHistoryItem(
            id=db_compare.id,
            position=PositionItem(
                id=db_compare.position_id,
                name=db_position.position_name if db_position else "",

            ),
            resume_ids=db_compare.resume_ids or [],
            candidate_count=len(db_compare.resume_ids or []),
            has_ai_analysis=bool(db_compare.ai_analysis),
            has_ranking=bool(db_compare.ranking),
            top_ranked_candidate=top_ranked_candidate,
            top_ranked_score=top_ranked_score,
            best_choice=recommendation.get("best_choice"),
            best_choice_reason=recommendation.get("reason"),
            created_at=db_compare.created_at
        )
        items.append(item)

    data=ComparisonListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )
    return success_response(message="获取对比历史成功",data=data)

@router.get("/{id}",summary="获取对比详情")
def get_compare_detail(id:int,db:Session=Depends(get_db)):
    db_compare=get_compare(id,db)
    if not db_compare:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对比记录不存在")

    comparison_data = db_compare.comparison_data or {}
    position_data = comparison_data.get("position") or {}
    candidates_data = comparison_data.get("candidates") or []

    result = ComparisonDetailResponse(
        id=db_compare.id,
        position=PositionItem(**position_data),
        candidates=[CandidateItem(**item) for item in candidates_data],
        ai_analysis=db_compare.ai_analysis,
        ranking=[ComparisonRankingItem(**item) for item in (db_compare.ranking or [])],
        created_at=db_compare.created_at
    )

    return success_response(message="获取对比详情成功", data=result)

@router.get("/{id}/export",summary="导出报告")
def export_compare_report(id:int,db:Session=Depends(get_db)):
    pdf_path=build_compare_report_pdf(id,db)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"candidate_comparison_{id}.pdf"
    )



