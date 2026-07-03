import tempfile
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.crud.resume import get_resume_by_id, update_parse_status, update_resume_parse_result
from app.database import SessionLocal
from app.services.resume_contact_ocr import enrich_resume_text_with_pdf_contact, merge_contact_result
from app.services.resume_embedding import build_resume_embedding_text, embed_resume_text
from app.services.resume_llm import extract_resume_structured_data
from app.services.resume_text_extractor import extract_resume_text
from app.storage.milvus_storage import insert_resume_embedding, delete_resume_embedding_by_resume_id
from app.storage.minio_storage import download_resume_file


#解析简历
def parse_resume_mock(resume_id:int):
    db=SessionLocal() #创建自己内部的跟数据库的会话
    try:
        resume = get_resume_by_id(db, resume_id)
        if not resume:
            # 这种HTTP的错误，最好在api层抛，其他层处理的是业务逻辑
            # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="没有该简历")
            return
        update_parse_status(db, resume_id, 1)
        db.commit()

        #下面是真正的解析，要先创建临时目录下载minio中对应的文件，然后放入解析代码，先得到文本内容
        with tempfile.TemporaryDirectory(prefix="resume_parse_") as temp_dir:
            local_file_path=Path(temp_dir)/resume.file_name

            download_resume_file(
                object_name=resume.file_path,
                target_path=str(local_file_path)
            )
            resume_text=extract_resume_text(
                file_path=str(local_file_path),
                file_type=resume.file_type
            )
            if resume.file_type == "pdf":
                resume_text = enrich_resume_text_with_pdf_contact(str(local_file_path), resume_text)

            structured_result=extract_resume_structured_data(resume_text)#得到结构化结果--pydantic
            structured_result = merge_contact_result(structured_result, resume_text)
            #将特殊类型解析为list[dict]
            work_experience=([item.model_dump() for item in structured_result.work_experience]
            if structured_result.work_experience else None)

            project_experience = ([item.model_dump() for item in structured_result.project_experience]
                               if structured_result.project_experience else None)

            education_experience = ([item.model_dump() for item in structured_result.education_experience]
                               if structured_result.education_experience else None)


        update_resume_parse_result(
            db,
            resume_id=resume_id,
            candidate_name=structured_result.candidate_name,
            phone=structured_result.phone,
            email=structured_result.email,
            education=structured_result.education,
            school=structured_result.school,
            major=structured_result.major,
            work_years=structured_result.work_years,
            current_company=structured_result.current_company,
            current_position=structured_result.current_position,
            skills=structured_result.skills,
            work_experience=work_experience,
            project_experience=project_experience,
            education_experience=education_experience,
            resume_summary=structured_result.resume_summary,
            original_content=resume_text,
            parse_status=2
        )
        resume=get_resume_by_id(db,resume.id)
        embedding_text = build_resume_embedding_text(resume)
        embedding = embed_resume_text(embedding_text)
        delete_resume_embedding_by_resume_id(resume_id)
        milvus_id = insert_resume_embedding(resume_id, embedding)
        resume.milvus_id=str(milvus_id)
        db.commit()
    except Exception as e:
        db.rollback()
        update_parse_status(db,resume_id,3)
        db.commit()
        print(f"简历解析失败，resume_id={resume_id},error={e}")
    finally:
        db.close()
