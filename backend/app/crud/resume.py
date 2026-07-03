from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.crud.position import get_position_by_id
from app.models import Resume

#创建简历
def create_resume(db:Session,*,candidate_name:str,file_path:str,file_name:str,file_type:str,file_size:int |None=None,position_id:int | None=None) -> Resume:
    resume=Resume(candidate_name=candidate_name,file_path=file_path,file_name=file_name,file_type=file_type,
                  file_size=file_size,position_id=position_id,status=1,parse_status=0,is_deleted=0)
    db.add(resume)
    db.flush()
    db.refresh(resume)
    return resume

#批量修改简历的状态
def batch_update_resume_status(resume_ids:list[int],status:int,db:Session):
    result=(
        db.query(Resume).filter(Resume.id.in_(resume_ids),Resume.is_deleted==0)
        .update(
            {Resume.status:status},
            synchronize_session=False
        )
    )
    return result

#根据简历ID查询简历
def get_resume_by_id(db:Session,resume_id:int) -> Resume | None:
    return db.query(Resume).filter(Resume.id==resume_id,Resume.is_deleted==0).first()

#更新解析状态
def update_parse_status(db:Session,resume_id:int,parse_status:int)-> Resume |None:
    resume=get_resume_by_id(db,resume_id)
    if resume:
        resume.parse_status=parse_status
    return resume

#更新解析结果
def update_resume_parse_result(
        db:Session,resume_id:int,*,
        candidate_name:str|None=None,
        phone:str|None=None,
        email:str|None=None,
        education:str|None=None,
        school:str|None=None,
        major:str|None=None,
        work_years:int |None=None,
        current_company:str|None=None,
        current_position:str|None=None,
        skills=None,
        work_experience=None,
        project_experience=None,
        education_experience=None,
        resume_summary:str|None=None,
        original_content:str|None=None,
        parse_status:int =2
)->Resume|None:
    resume=get_resume_by_id(db,resume_id)
    if not resume:
        return None
    if candidate_name is not None:
        resume.candidate_name=candidate_name
    if original_content is not None:
        resume.original_content=original_content

    if phone is not None:
        resume.phone = phone

    if email is not None:
        resume.email = email

    if education is not None:
        resume.education = education

    if school is not None:
        resume.school = school

    if major is not None:
        resume.major = major

    if work_years is not None:
        resume.work_years = work_years

    if current_company is not None:
        resume.current_company = current_company

    if current_position is not None:
        resume.current_position = current_position

    if skills is not None:
        resume.skills = skills

    if work_experience is not None:
        resume.work_experience = work_experience

    if project_experience is not None:
        resume.project_experience = project_experience

    if education_experience is not None:
        resume.education_experience = education_experience

    if resume_summary is not None:
        resume.resume_summary = resume_summary

    if original_content is not None:
        resume.original_content = original_content

    resume.parse_status=parse_status
    return resume

#更新状态
def update_status(id:int,status:int,db:Session):
    resume=get_resume_by_id(db,id)
    if resume:
        resume.status=status
        db.flush()
    return resume

#软删除
def delete_resume(id:int,db:Session):
    db_resume=get_resume_by_id(db,id)
    if not db_resume:
        return None
    db_resume.is_deleted=1
    return db_resume

#分页查询
def get_resume_list(page:int,page_size:int,db:Session,
                       keyword:str|None=None,position_id:int|None=None,
                       education:str|None=None,work_years_min:int|None=None,
                       work_years_max:int|None=None,status:int|None=None):
    query=db.query(Resume).filter(Resume.is_deleted==0)
    if keyword:
        like_keyword=f"%{keyword}%"
        query=query.filter(
            or_(
                Resume.candidate_name.like(like_keyword),
                Resume.phone.like(like_keyword),
                Resume.current_company.like(like_keyword),
                Resume.current_position.like(like_keyword),
            )
        )
    if position_id:
        query=query.filter(Resume.position_id==position_id)

    if education:
        query=query.filter(Resume.education==education)

    if work_years_min:
        query=query.filter(Resume.work_years>=work_years_min)

    if work_years_max:
        query=query.filter(Resume.work_years<=work_years_max)

    if status:
        query=query.filter(Resume.status==status)

    total=query.count()

    data=(
        query.order_by(Resume.created_at.desc())
        .offset((page-1)*page_size)
        .limit(page_size)
        .all()
    )

    return total,data

def get_resumes_by_ids(ids:list[int],db:Session):
    return (
        db.query(Resume).filter(Resume.id.in_(ids),Resume.is_deleted==0)
        .all()
    )

#绑定岗位
def bind_position(id:int,position_id:int,db:Session):
    db_resume=get_resume_by_id(db,id)
    if not db_resume:
        return None
    db_position=get_position_by_id(position_id,db)
    if not db_position:
        return None
    db_resume.position_id=position_id
    return db_resume

