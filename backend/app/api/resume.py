import shutil
import tempfile
import zipfile
from typing import List, Optional, Annotated
from pathlib import Path
from urllib.parse import quote
from fastapi.responses import StreamingResponse,FileResponse
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from starlette import status
from starlette.status import HTTP_404_NOT_FOUND
from app.crud import position, resume
from app.schemas.resume import UploadResumesResponse, ResumeUploadResult,ResumeStatusRequest
from app.crud.resume import create_resume
from app.database import get_db
from app.models import Resume
from app.schemas.resume import ParseUploadFile, ResumeDetailResponse, ResumeListItemResponse, ResumeBatchDownloadRequest, \
    ResumeBindStatusRequest
from app.services.resume_embedding import build_resume_embedding_text
from app.services.resume_parse import parse_resume_mock
from app.storage.minio_storage import upload_resume_file, get_resume_file_stream, download_resume_file,delete_resume_file
from app.utils.response import success_response
from app.schemas.resume import ResumeListResponse,ResumeListRequest
import os

router = APIRouter(prefix="/api/v1/resumes", tags=["简历模块"])

ALLOWED_SUFFIXES = {".pdf", ".docx"}

#Minio存放文件的类型
CONTENT_TYPE_MAP = {
      ".pdf": "application/pdf",
      ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  }

RESUME_STATUS_MAP={
    1:"待筛选",
    2:"待沟通",
    3:"已淘汰",
    4:"已通过"
}

PARSE_STATUS_MAP = {
      0: "待解析",
      1: "解析中",
      2: "已完成",
      3: "解析失败",
  }


# 上传简历
@router.post("/upload", summary="上传简历")
def upload_resumes(
        background_tasks:BackgroundTasks,
        files: Annotated[list[UploadFile],File(description="简历文件列表")],
        position_id: Annotated[Optional[int],Form( description="关联岗位ID")]=None,
        db: Session = Depends(get_db)
):
    #1.先判断是不是文件
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请至少上传一个文件")
    results=[]
    #2.将文件和压缩包的文件放在一起，形成一个文件列表
    #创建一个临时文件，存放解压后的文件和文件，with是上下文管理器，用完自动清除
    with tempfile.TemporaryDirectory(prefix="resume_upload") as temp_dir:
        parsed_files = expend_upload_files(files, temp_dir)
        #上面已经得到了扩展后的文件，
        for item in parsed_files:
            result=process_single_resume_file(item,position_id,db,background_tasks)
            results.append(result)

    success_count=sum(1 for item in results if item.status =="success")
    failed_count=sum(1 for item in results if item.status =="failed")
    data=UploadResumesResponse(
        total=len(results),
        success=success_count,
        failed=failed_count,
        results=results
    )
    return success_response(message="上传成功",data=data)

#获取简历列表
@router.get("",response_model=ResumeListResponse,summary="获取简历列表")
#这里注意，虽然data是前端传入的参数，但是因为get请求没有请求体，所以这里要加Depends，加了后FastAPI
#会按照依赖解析为Query参数，在url路径中
def get_resume_detail(data:ResumeListRequest=Depends(),db:Session=Depends(get_db)):
    total,db_data=resume.get_resume_list(data.page,data.page_size,db,data.keyword,data.position_id,data.education
                                         ,data.work_years_min,data.work_years_max,data.status)
    if total==0:
        return success_response(message="没有匹配的简历")
    items=[]
    for item in db_data:
        items.append(
            ResumeListItemResponse(
                id=item.id,
                candidate_name=item.candidate_name,
                phone=item.phone,
                education=item.education,
                work_years=item.work_years,
                current_company=item.current_company,
                position_id=item.position_id,
                status=item.status,
                status_name=RESUME_STATUS_MAP.get(item.status, "未知"),
                parse_status=item.parse_status,
                parse_status_name=PARSE_STATUS_MAP.get(item.parse_status, "未知"),
                created_at=item.created_at
            )
        )
    result=ResumeListResponse(
        total=total,
        page=data.page,
        page_size=data.page_size,
        data=items
    )
    return success_response(message="获取简历列表成功",data=result)


#获取简历详情
@router.get("/{id}",summary="获取简历详情")
def get_resume_detail(id:int,db:Session=Depends(get_db)):
    db_resume=resume.get_resume_by_id(db,id)
    if not db_resume:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,detail="简历不存在")
    position_data=None
    if db_resume.position_id:
        db_position = position.get_position_by_id(db_resume.position_id, db)
        if db_position:
            position_data={
                "id":db_position.id,
                "name":db_position.position_name
            }
    data = {
        "id": db_resume.id,
        "candidate_name": db_resume.candidate_name,
        "phone": db_resume.phone,
        "email": db_resume.email,
        "education": db_resume.education,
        "school": db_resume.school,
        "major": db_resume.major,
        "work_years": db_resume.work_years,
        "current_company": db_resume.current_company,
        "current_position": db_resume.current_position,
        "skills": db_resume.skills,
        "work_experience": db_resume.work_experience,
        "project_experience": db_resume.project_experience,
        "education_experience": db_resume.education_experience,
        "resume_summary": db_resume.resume_summary,
        "position": position_data,
        "status": db_resume.status,
        "status_name": RESUME_STATUS_MAP.get(db_resume.status, "未知"),
        "parse_status": db_resume.parse_status,
        "parse_status_name": PARSE_STATUS_MAP.get(db_resume.parse_status, "未知"),
        "created_at": db_resume.created_at,
    }
    result = ResumeDetailResponse.model_validate(data)
    return success_response(message="获取简历详情成功",data=result)

#下载简历
@router.get("/{id}/download",summary="下载简历")
def download_resume(id:int,db:Session=Depends(get_db)):
    db_resume =resume.get_resume_by_id(db,id)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="简历不存在")

    object_name=db_resume.file_path
    file_name=db_resume.file_name

    file_stream=get_resume_file_stream(object_name)

    encoded_file_name=quote(file_name)

    headers={
        "Content-Disposition":f"attachment; filename*=UTF-8''{encoded_file_name}"
    }

    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers=headers
    )

#批量下载
@router.post("/batch-download",summary="批量下载简历")
def batch_download(data:ResumeBatchDownloadRequest,background_tasks:BackgroundTasks,db:Session=Depends(get_db)):
    db_ids=data.ids
    if not db_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="没有传入需要下载的简历")
    db_resumes=[]
    for id in db_ids:
        db_resume=resume.get_resume_by_id(db,id)
        if not db_resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"未找到简历ID为{id}的简历")
        db_resumes.append(db_resume)

    #下载完了，先找到存放路径，和压缩进压缩包
    temp_dir=tempfile.mkdtemp(prefix="resume_batch_")
    zip_path=os.path.join(temp_dir,"resume.zip")

    for item in db_resumes:
        local_file_path=os.path.join(temp_dir,f"{item.id}_{item.file_name}")
        download_resume_file(
            object_name=item.file_path,
            target_path=local_file_path
        )
    #已经将简历下载到了temp_dir，但是还没有压缩
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
        for file_path in Path(temp_dir).iterdir():
            if file_path.name=="resume.zip":
                #压缩包也在里面，不读取压缩包的
                continue
            if file_path.is_file():
                zf.write(file_path,arcname=file_path.name)

    def cleanup():
        shutil.rmtree(temp_dir,ignore_errors=True)

    background_tasks.add_task(cleanup)

    encoded_file_name=quote("建立批量下载.zip")

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename="简历批量下载.zip",
        headers={
            "Content-Disposition":f"attachment;filename*=UTF-8''{encoded_file_name}"
        }
    )

#删除简历 --还要删除minio中的记录 --软删除
@router.delete("/{id}",summary="删除简历")
def delete_resume(id:int,db:Session=Depends(get_db)):
    db_resume=resume.get_resume_by_id(db,id)
    if not db_resume:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,detail="简历不存在")
    if db_resume.file_path:
        delete_resume_file(db_resume.file_path)

    resume.delete_resume(id,db)
    db.commit()
    return success_response(message="删除简历成功")

#关联岗位
@router.put("/{id}/bindPosition",summary="关联岗位")
def bind_position(id:int,position_id:ResumeBindStatusRequest,db:Session=Depends(get_db)):
    db_resume=resume.bind_position(id,position_id.position_id,db)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="简历或岗位不存在")

    db.commit()
    db.refresh(db_resume)
    return success_response(message="关联岗位成功")



#更新状态
@router.patch("/{id}/status",summary="更新状态")
def update_status(id:int,status:ResumeStatusRequest,db:Session=Depends(get_db)):
    db_resume =resume.update_status(id,status.status,db)
    if not db_resume:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,detail="简历不存在")
    db.commit()
    db.refresh(db_resume)
    return success_response(message=f"更新状态为{status}")



#重新解析--肯定要先删除简历目前的解析部分
@router.post("/{id}/reparse",summary="重新解析")
def reparse_resume(id:int,background_tasks:BackgroundTasks,db:Session=Depends(get_db)):
    db_resume=resume.get_resume_by_id(db,id)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="简历不存在")
    db_resume.parse_status=0
    db.commit()
    background_tasks.add_task(parse_resume_mock,id)
    return success_response(message="重新解析任务已提交")



#展开文件，有压缩包的话将文件展开和其他文件放一起
def expend_upload_files(files:List[UploadFile],temp_dir:str) -> List[ParseUploadFile]:
    parsed_files=[]
    for upload_file in files:
        file_name=upload_file.filename or "unknown"
        suffix=Path(file_name).suffix.lower()

        if suffix==".zip":
            zip_path=Path(temp_dir)/file_name
            #现在是将zip文件放入了zip_path的文件夹中
            with zip_path.open("wb") as f:
                shutil.copyfileobj(upload_file.file,f)
            #创建解析后的文件夹
            extract_dir=Path(temp_dir)/Path(file_name).stem
            extract_dir.mkdir(parents=True,exist_ok=True)
            #开始解析，解析之后放入创建的文件夹中
            with zipfile.ZipFile(zip_path,"r") as zf:
                zf.extractall(extract_dir)

            #遍历文件夹
            for extract_file in extract_dir.rglob("*"):
                if extract_file.is_file(): #如果是文件
                    parsed_files.append(
                        ParseUploadFile(
                            file_name=extract_file.name,
                            content_type=None,
                            source_type="zip",
                            temp_path=str(extract_file)
                        )
                    )

        else:#如果直接是文件不是zip
            file_path=Path(temp_dir)/file_name

            with file_path.open("wb") as f:
                shutil.copyfileobj(upload_file.file,f)
                parsed_files.append(
                    ParseUploadFile(
                        file_name=file_name,
                        content_type=None,
                        source_type="file",
                        temp_path=str(file_path)
                    )
                )

    return parsed_files

#格式校验
def process_single_resume_file(
        item:ParseUploadFile,
        position_id:Optional[int],
        db:Session,
        background_tasks:BackgroundTasks
) -> ResumeUploadResult:
    suffix=Path(item.file_name).suffix.lower()

    if suffix not in ALLOWED_SUFFIXES:
        return ResumeUploadResult(
            file_name=item.file_name,
            status="failed",
            error="不支持的文件格式"
        )
    file_bytes=Path(item.temp_path).read_bytes()
    object_name=upload_resume_file(
        file_bytes=file_bytes,
        file_name=item.file_name,
        content_type=CONTENT_TYPE_MAP.get(suffix)
    )
    resume=create_resume(db=db,candidate_name="待解析",file_path=object_name,
                         file_name=item.file_name,file_type=suffix.replace(".",""),
                         # file_size=Path(item.temp_path).stat().st_size,
                         file_size=len(file_bytes),
                         position_id=position_id)
    db.commit()
    db.refresh(resume)
    background_tasks.add_task(parse_resume_mock,resume.id)
    return ResumeUploadResult(
        file_name=item.file_name,
        status="success",
        resume_id=resume.id
    )

