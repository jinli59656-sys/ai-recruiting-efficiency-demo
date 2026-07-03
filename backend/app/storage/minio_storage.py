from datetime import datetime
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from minio import Minio
from sqlalchemy.sql.functions import now

from app.config import settings


#1.获取minio客户端
def get_minio_client()->Minio:
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )


#2.生成对象名
def build_resume_object_name(file_name:str)->str:
    now=datetime.now()
    suffix=Path(file_name).suffix #获取文件的后缀名
    stem=Path(file_name).stem.replace(" ","_") #去掉文件后缀，并且把文件名中的空格换成_
    return f"resumes/{now:%Y}/{now:%m}/{uuid4().hex}_{stem}{suffix}"

def build_recording_object_name(file_name:str):
    now=datetime.now()
    suffix=Path(file_name).suffix
    stem=Path(file_name).stem.replace(" ","_") #去掉文件后缀，并且把文件名中的空格换成_
    return f"recordings/{now:%Y}/{now:%m}/{uuid4().hex}_{stem}{suffix}"

#3.1 上传文件
def upload_resume_file(file_bytes:bytes,file_name:str,content_type:str |None=None):
    client=get_minio_client()
    object_name=build_resume_object_name(file_name)

    client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
        data=BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=content_type or "application/octet-stream"
    )
    return object_name

#3.2 上传录音文件
def upload_recording_file(file_bytes:bytes,file_name:str,content_type:str|None=None):
    client=get_minio_client()
    object_name=build_recording_object_name(file_name)

    client.put_object(
        bucket_name=settings.MINIO_BUCKET1,
        object_name=object_name,
        data=BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=content_type or "application/octet-stream"
    )
    return object_name

#4.需要的时候从minio下载出文件，进行文本解析
def download_resume_file(object_name:str,target_path:str):
    """
    object_name文件在minio中的名字，可以拼接形成url路径
    target_path将文件下载到我指定的路径
    """
    client=get_minio_client()
    #这个方法写了object_name就自动拼接下载路径去下载
    client.fget_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
        file_path=target_path
    )

#4.1 下载录音文件
def download_recording_file(object_name:str,target_path:str):
    client=get_minio_client()
    client.fget_object(
        bucket_name=settings.MINIO_BUCKET1,
        object_name=object_name,
        file_path=target_path
    )

#下载文件返回给前端返回的是文件流
def get_resume_file_stream(object_name:str):
    client=get_minio_client()
    return client.get_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name
    )

#之前返回的是简历流，现在返回录音流
def get_recording_file_stream(object_name:str):
    client=get_minio_client()
    return client.get_object(
        bucket_name=settings.MINIO_BUCKET1,
        object_name=object_name
    )

#删除minio中的文件
def delete_resume_file(object_name:str):
    client=get_minio_client()
    client.remove_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name
    )
