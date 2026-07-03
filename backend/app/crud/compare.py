from sqlalchemy.orm import Session

from app.models.compare import CandidateComparison


def get_compare(id:int,db:Session):
    db_compare =db.query(CandidateComparison).filter(CandidateComparison.id==id).first()
    return db_compare




def get_compare_history(db:Session,page:int=1,page_size:int=10,position_id:int|None=None):
    query=db.query(CandidateComparison)
    if position_id:
        query=query.filter(CandidateComparison.position_id==position_id)

    total=query.count()

    items=(
        query.order_by(CandidateComparison.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return total,items