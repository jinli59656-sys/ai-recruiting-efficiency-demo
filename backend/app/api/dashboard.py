from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import JobPosition, Resume, InterviewRecording, InterviewSummary
from models.evaluations import InterviewEvaluation
from models.intake import RecruitmentDocRow, RecruitmentMessage, RecruitmentSyncEvent
from schemas.dashboard import DashboardTodoItem, DashboardInterviewItem, DashboardActivityItem, DashboardStats, \
    DashboardOverviewResponse
from utils.response import success_response

router=APIRouter(prefix="/api/v1/dashboard",tags=["工作台"])

TRANSCRIPT_STATUS_NAME_MAP = {
      0: "未转写",
      1: "转写中",
      2: "已完成",
      3: "失败"
  }

@router.get("/overview", summary="获取工作台概览")
def get_dashboard_overview(db: Session = Depends(get_db)):
    #开放岗位数
    open_positions = db.query(JobPosition).filter(
        JobPosition.status == 1,
        JobPosition.is_deleted == 0
    ).count()

    #简历总数
    resume_total = db.query(Resume).filter(Resume.is_deleted == 0).count()

    #待筛选简历
    pending_resumes = db.query(Resume).filter(
        Resume.is_deleted == 0,
        Resume.status == 1
    ).count()

    #面试中候选人
    interviewing_count = db.query(InterviewRecording).filter(
        InterviewRecording.transcript_status.in_([0, 1])
    ).count()

    #待转写录音数
    pending_recordings = db.query(InterviewRecording).filter(
        InterviewRecording.transcript_status == 0
    ).count()

    #待生成摘要数
    summary_recording_ids = {
        item.recording_id
        for item in db.query(InterviewSummary.recording_id).all()
    }

    completed_recordings = db.query(InterviewRecording).filter(
        InterviewRecording.transcript_status == 2
    ).all()
    #这里面已完成转写但是不在已生成摘要的 就是要的结果
    pending_summaries = sum(
        1 for item in completed_recordings if item.id not in summary_recording_ids
    )

    #待生成评价数
    evaluation_summary_ids = {
        item.summary_id
        for item in db.query(InterviewEvaluation.summary_id).all()
    }
    all_summaries = db.query(InterviewSummary).all()
    #已经有面试摘要还没评价的
    pending_evaluations = sum(
        1 for item in all_summaries if item.id not in evaluation_summary_ids
    )

    today = func.current_date()
    intake_today = db.query(RecruitmentMessage).filter(
        func.date(RecruitmentMessage.created_at) == today
    ).count()
    doc_synced_total = db.query(RecruitmentDocRow).filter(
        RecruitmentDocRow.sync_status == "synced"
    ).count()
    needs_review_total = db.query(RecruitmentDocRow).filter(
        RecruitmentDocRow.needs_review == True
    ).count()
    pending_interviews = db.query(RecruitmentDocRow).filter(
        RecruitmentDocRow.stage.in_(["初面", "一面", "复试", "二面", "终面"])
    ).count()

    #拼返回
    todos = []

    if pending_resumes > 0:
        todos.append(DashboardTodoItem(title=f"待筛选简历 {pending_resumes} 份", type="resume_pending"))

    if pending_recordings > 0:
        todos.append(DashboardTodoItem(title=f"待转写录音 {pending_recordings} 条", type="recording_pending"))

    if pending_summaries > 0:
        todos.append(DashboardTodoItem(title=f"待生成摘要 {pending_summaries} 条", type="summary_pending"))

    if pending_evaluations > 0:
        todos.append(DashboardTodoItem(title=f"待生成评价 {pending_evaluations} 条", type="evaluation_pending"))

    if needs_review_total > 0:
        todos.append(DashboardTodoItem(title=f"需确认招聘数据 {needs_review_total} 条", type="intake_review"))

    recent_interviews = []

    db_recordings = (
        db.query(InterviewRecording)
        .order_by(InterviewRecording.created_at.desc())
        .limit(5)
        .all()
    )

    for item in db_recordings:
        db_resume = db.query(Resume).filter(Resume.id == item.resume_id).first()
        db_position = db.query(JobPosition).filter(
            JobPosition.id == item.position_id).first() if item.position_id else None

        recent_interviews.append(
            DashboardInterviewItem(
                recording_id=item.id,
                candidate_name=db_resume.candidate_name if db_resume else "未知候选人",
                position_name=db_position.position_name if db_position else None,
                interview_date=str(item.interview_date) if item.interview_date else None,
                transcript_status_name=TRANSCRIPT_STATUS_NAME_MAP.get(item.transcript_status)
            )
        )

    #最近摘要
    recent_summaries = (
        db.query(InterviewSummary)
        .order_by(InterviewSummary.created_at.desc())
        .limit(3)
        .all()
    )

    #最近评价
    recent_evaluations = (
        db.query(InterviewEvaluation)
        .order_by(InterviewEvaluation.created_at.desc())
        .limit(3)
        .all()
    )

    recent_sync_events = (
        db.query(RecruitmentSyncEvent)
        .order_by(RecruitmentSyncEvent.created_at.desc())
        .limit(5)
        .all()
    )

    #拼接最近活动状态
    recent_activities = []

    for item in recent_summaries:
        recent_activities.append(
            DashboardActivityItem(
                title=f"录音 {item.recording_id} 的面试摘要已生成",
                time=str(item.created_at)
            )
        )

    for item in recent_evaluations:
        recent_activities.append(
            DashboardActivityItem(
                title=f"候选人 {item.resume_id} 的面试评价已生成",
                time=str(item.created_at)
            )
        )

    for item in recent_sync_events:
        recent_activities.append(
            DashboardActivityItem(
                title=item.title,
                time=str(item.created_at)
            )
        )

    stats = DashboardStats(
        open_positions=open_positions,
        resume_total=resume_total,
        pending_resumes=pending_resumes,
        interviewing_count=interviewing_count,
        intake_today=intake_today,
        doc_synced_total=doc_synced_total,
        needs_review_total=needs_review_total,
        pending_interviews=pending_interviews
    )
    recent_activities.sort(key=lambda x: x.time, reverse=True)
    recent_activities = recent_activities[:5]
    data = DashboardOverviewResponse(
        stats=stats,
        todos=todos,
        recent_interviews=recent_interviews,
        recent_activities=recent_activities
    )

    return success_response(message="获取工作台概览成功", data=data)

