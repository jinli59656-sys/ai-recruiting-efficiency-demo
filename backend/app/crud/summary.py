import json

from sqlalchemy.orm import Session

from models import InterviewSummary
from schemas.summary import UpdateSummaryRequest

def get_summary_by_id(id:int,db:Session):
    db_summary=db.query(InterviewSummary).filter(InterviewSummary.id==id).first()
    return db_summary

def get_summary_by_recording_id(recording_id:int,db:Session):
    db_summary=db.query(InterviewSummary).filter(InterviewSummary.recording_id==recording_id).first()
    return db_summary

#更新摘要
def update_summary(id:int,data:UpdateSummaryRequest,db:Session):
    db_summary=db.query(InterviewSummary).filter(InterviewSummary.id==id).first()
    if not db_summary:
        return None
    if  data.summary_overview:
        db_summary.summary_overview=json.dumps(data.summary_overview,ensure_ascii=False)
    if  data.key_qa:
        #这里是放入库中要将python对象转为str，取出就是将str转为python就是json.loads()
        db_summary.key_qa = json.dumps(  # json.dumps(...,ensure_ascii=False)  将python对象转为json字符串 表示的是中文不用acsii编码
            [item.model_dump() for item in data.key_qa],  # 以json格式放入，本质还是字符串
            ensure_ascii=False
        )
    if  data.technical_skills:
        db_summary.technical_skills=json.dumps(data.technical_skills)
    if data.soft_skills:
        db_summary.soft_skills=json.dumps(data.soft_skills)
    if data.highlights:
        db_summary.highlights=json.dumps(data.highlights)
    if data.concerns:
        db_summary.concerns=json.dumps(data.concerns)
    if data.candidate_questions:
        db_summary.candidate_questions=json.dumps(data.candidate_questions)
    db.flush()
    return db_summary

def get_recording_by_summary_id(id:int,db:Session):
    db_summary=db.query(InterviewSummary).filter(InterviewSummary.id==id).first()
    return db_summary.recording_id

