from sqlalchemy.orm import Session

from models.evaluations import InterviewEvaluation


def get_evaluation_by_summary_id(summary_id:int,db:Session):
    db_evaluation=db.query(InterviewEvaluation).filter(InterviewEvaluation.summary_id==summary_id).first()
    return db_evaluation

def get_evaluation_by_id(id:int,db:Session):
    db_evaluation=db.query(InterviewEvaluation).filter(InterviewEvaluation.id==id).first()
    return db_evaluation

def get_evaluation_by_resume_id(resume_id:int,db:Session):
    db_evaluation=db.query(InterviewEvaluation).filter(InterviewEvaluation.resume_id==resume_id).first()
    return db_evaluation

def add_evaluation_hr_comment(id:int,hr_comment:str,db:Session):
    db_evaluation=db.query(InterviewEvaluation).filter(InterviewEvaluation.id==id).first()
    if not db_evaluation:
        return None
    db_evaluation.hr_comment=hr_comment
    db.flush()
    return db_evaluation

def get_evaluations_by_resume_id(resume_id:int,db:Session):
    query=db.query(InterviewEvaluation).filter(InterviewEvaluation.resume_id==resume_id)
    return query.count(),query.all()

def get_evaluation_by_recording_id(recording_id:int,db:Session):
    db_evaluation=db.query(InterviewEvaluation).filter(InterviewEvaluation.recording_id==recording_id).first()
    return db_evaluation