from pydantic import BaseModel


#统计卡片
class DashboardStats(BaseModel):
    open_positions: int
    resume_total: int
    pending_resumes: int
    interviewing_count: int
    intake_today: int = 0
    doc_synced_total: int = 0
    needs_review_total: int = 0
    pending_interviews: int = 0

#待办事项
class DashboardTodoItem(BaseModel):
    title: str
    type: str

#最近面试
class DashboardInterviewItem(BaseModel):
    recording_id: int
    candidate_name: str
    position_name: str | None = None
    interview_date: str | None = None
    transcript_status_name: str | None = None

#最近动态
class DashboardActivityItem(BaseModel):
    title: str
    time: str

#顶层
class DashboardOverviewResponse(BaseModel):
    stats: DashboardStats
    todos: list[DashboardTodoItem]
    recent_interviews: list[DashboardInterviewItem]
    recent_activities: list[DashboardActivityItem]


