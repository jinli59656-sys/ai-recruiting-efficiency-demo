import json

from sqlalchemy.orm import Session

from app.models.question import InterviewQuestion
from app.schemas.question import QuestionUpdateRequest


def create_question(position_id,resume_id,question_type,difficulty,question_content,reference_answer,scoring_points,
                    source,db:Session
):
    db_question=InterviewQuestion(
        position_id=position_id,resume_id=resume_id,question_type=question_type,
        difficulty=difficulty,question_content=question_content,
        reference_answer=reference_answer,scoring_points=scoring_points,
        source=source,is_saved=0
    )
    db.add(db_question)
    db.flush()
    return db_question

def get_question_list(page:int,page_size:int,db:Session):
    query=db.query(InterviewQuestion)
    total=query.count()

    items=(
        query.order_by(InterviewQuestion.created_at.desc())
        .offset((page-1)*page_size)
        .limit(page_size)
        .all()
    )
    return total,items

def update_question(id:int,data:QuestionUpdateRequest,db:Session):
    #根据传入的值进行赋值操作
    db_question=db.query(InterviewQuestion).filter(InterviewQuestion.id==id).first()
    if db_question:
        new_data=data.model_dump(exclude_unset=True)
        if "type" in new_data:
            db_question.question_type = new_data["type"]

        if "difficulty" in new_data:
            db_question.difficulty = new_data["difficulty"]

        if "question" in new_data:
            db_question.question_content = new_data["question"]

        if "reference_answer" in new_data:
            db_question.reference_answer = new_data["reference_answer"]

        if "scoring_points" in new_data:
            db_question.scoring_points = json.dumps(new_data["scoring_points"], ensure_ascii=False)

        if "source" in new_data:
            db_question.source = new_data["source"]
    db.flush()
    return db_question

#删除题目
def delete_question(id:int,db:Session):
    db_question=db.query(InterviewQuestion).filter(InterviewQuestion.id==id).first()
    if not db_question:
        return None
    db.delete(db_question)
    return db_question

#批量修改保存状态
def save_batch(ids:list[int],db:Session):
    result=(
        db.query(InterviewQuestion).filter(InterviewQuestion.id.in_(ids))
        .update(
            {InterviewQuestion.is_saved:1},
            synchronize_session=False
        )
    )
    return result
