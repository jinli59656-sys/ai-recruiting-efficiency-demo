from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.intake import RecruitmentDocRow, RecruitmentMessage, RecruitmentSyncEvent
from schemas.intake import IntakeEventItem, IntakeMessageItem, IntakeParseRequest, TencentDocRowItem
from services.intake import parse_and_sync_message
from utils.response import success_response

router = APIRouter(prefix="/api/v1/intake", tags=["招聘数据采集"])


@router.post("/messages/parse", summary="解析企业微信群招聘消息并同步")
def parse_message(data: IntakeParseRequest, db: Session = Depends(get_db)):
    result = parse_and_sync_message(
        db=db,
        raw_message=data.raw_message,
        source_channel=data.source_channel,
        sender=data.sender,
    )
    return success_response(message="解析并同步成功", data=result)


@router.get("/messages", summary="获取已解析招聘消息")
def get_messages(limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(RecruitmentMessage)
        .order_by(RecruitmentMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    data = [IntakeMessageItem.model_validate(item) for item in rows]
    return success_response(message="获取招聘消息成功", data=data)


@router.get("/tencent-docs", summary="获取腾讯在线文档镜像表")
def get_tencent_docs(limit: int = 100, db: Session = Depends(get_db)):
    rows = (
        db.query(RecruitmentDocRow)
        .order_by(RecruitmentDocRow.updated_at.desc())
        .limit(limit)
        .all()
    )
    data = [TencentDocRowItem.model_validate(item) for item in rows]
    return success_response(message="获取腾讯文档镜像成功", data=data)


@router.get("/events", summary="获取招聘数据同步事件")
def get_events(limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(RecruitmentSyncEvent)
        .order_by(RecruitmentSyncEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    data = [IntakeEventItem.model_validate(item) for item in rows]
    return success_response(message="获取同步事件成功", data=data)
