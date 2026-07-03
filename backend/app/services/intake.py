import re

from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from config import settings
from models.intake import RecruitmentDocRow, RecruitmentMessage, RecruitmentSyncEvent
from schemas.intake import IntakeParsedResult, IntakeParseResponse


STAGE_KEYWORDS = [
    "简历已收",
    "待筛选",
    "初面",
    "一面",
    "复试",
    "二面",
    "终面",
    "通过",
    "淘汰",
    "待反馈",
    "待安排复试",
]

POSITION_KEYWORDS = [
    "Java后端",
    "Java 后端",
    "后端开发",
    "Python后端",
    "前端开发",
    "产品经理",
    "测试工程师",
    "数据分析师",
    "算法工程师",
    "运维工程师",
    "HRBP",
]

EDUCATION_KEYWORDS = ["大专", "本科", "硕士", "博士"]


def parse_message_with_fallback(raw_message: str, source_channel: str, sender: str | None) -> IntakeParsedResult:
    text = raw_message.strip()
    candidate_name = extract_candidate_name(text)
    position_name = extract_position_name(text)
    stage = extract_stage(text)
    result = IntakeParsedResult(
        candidate_name=candidate_name or "待确认候选人",
        position_name=position_name,
        education=extract_education(text),
        work_years=extract_work_years(text),
        stage=stage,
        interview_time=extract_interview_time(text),
        interviewer=extract_interviewer(text),
        owner=sender or extract_owner(text),
        source_channel=source_channel or "企业微信-招聘群",
        raw_message=raw_message,
        confidence=0.55 if candidate_name and (position_name or stage) else 0.35,
        needs_review=True,
    )
    return result


def extract_with_ai(raw_message: str, source_channel: str, sender: str | None) -> IntakeParsedResult | None:
    if not settings.QWEN_API_KEY:
        return None

    prompt = f"""
你是招聘运营助手。请从企业微信群聊消息中抽取招聘流程数据，并严格输出结构化字段。

字段要求：
- candidate_name: 候选人姓名，无法判断时填“待确认候选人”
- position_name: 应聘岗位
- education: 学历，如大专/本科/硕士/博士
- work_years: 工作年限数字
- stage: 当前招聘阶段，如简历已收/待筛选/初面/一面/复试/终面/通过/淘汰/待反馈
- interview_time: 面试或跟进时间，保留原文表达
- interviewer: 面试官
- owner: 负责人，优先使用发送人
- source_channel: 来源渠道
- raw_message: 原始消息
- confidence: 0到1之间的小数
- needs_review: 低置信度或字段缺失时为true

来源渠道：{source_channel}
发送人：{sender or ""}
群聊消息：{raw_message}
"""
    try:
        llm = ChatOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL,
            model=settings.QWEN_MODEL,
            temperature=0,
        )
        structured_llm = llm.with_structured_output(IntakeParsedResult)
        result = structured_llm.invoke(prompt)
        parsed = IntakeParsedResult.model_validate(result)
        parsed.source_channel = source_channel or parsed.source_channel
        parsed.raw_message = raw_message
        parsed.owner = parsed.owner or sender
        parsed.needs_review = parsed.needs_review or parsed.confidence < 0.75
        return parsed
    except Exception:
        return None


def parse_recruitment_message(raw_message: str, source_channel: str, sender: str | None) -> IntakeParsedResult:
    return extract_with_ai(raw_message, source_channel, sender) or parse_message_with_fallback(
        raw_message=raw_message,
        source_channel=source_channel,
        sender=sender,
    )


def parse_and_sync_message(
    db: Session,
    raw_message: str,
    source_channel: str,
    sender: str | None,
) -> IntakeParseResponse:
    parsed = parse_recruitment_message(raw_message, source_channel, sender)

    db_message = RecruitmentMessage(
        raw_message=raw_message,
        source_channel=parsed.source_channel,
        sender=sender,
        candidate_name=parsed.candidate_name,
        position_name=parsed.position_name,
        education=parsed.education,
        work_years=parsed.work_years,
        stage=parsed.stage,
        interview_time=parsed.interview_time,
        interviewer=parsed.interviewer,
        owner=parsed.owner,
        confidence=parsed.confidence,
        needs_review=parsed.needs_review,
    )
    db.add(db_message)
    db.flush()

    doc_row = RecruitmentDocRow(
        message_id=db_message.id,
        candidate_name=parsed.candidate_name,
        position_name=parsed.position_name,
        stage=parsed.stage,
        interview_time=parsed.interview_time,
        owner=parsed.owner,
        source_channel=parsed.source_channel,
        sync_status="synced",
        needs_review=parsed.needs_review,
    )
    db.add(doc_row)
    db.flush()

    db.add(
        RecruitmentSyncEvent(
            message_id=db_message.id,
            doc_row_id=doc_row.id,
            event_type="message_parsed",
            title=f"已从{parsed.source_channel}解析候选人{parsed.candidate_name}",
            detail=raw_message,
        )
    )
    db.add(
        RecruitmentSyncEvent(
            message_id=db_message.id,
            doc_row_id=doc_row.id,
            event_type="doc_synced",
            title=f"已同步{parsed.candidate_name}至腾讯在线文档镜像表",
            detail=f"{parsed.position_name or '岗位待确认'} / {parsed.stage or '阶段待确认'}",
        )
    )
    if parsed.needs_review:
        db.add(
            RecruitmentSyncEvent(
                message_id=db_message.id,
                doc_row_id=doc_row.id,
                event_type="needs_review",
                title=f"{parsed.candidate_name}信息置信度较低，需人工确认",
                detail=f"confidence={parsed.confidence}",
            )
        )

    db.commit()
    db.refresh(db_message)
    db.refresh(doc_row)

    return IntakeParseResponse(
        message_id=db_message.id,
        doc_row_id=doc_row.id,
        sync_status=doc_row.sync_status,
        **parsed.model_dump(),
    )


def extract_candidate_name(text: str) -> str | None:
    cleaned = re.sub(r"@\S+\s*", "", text).strip()
    match = re.search(r"(?:候选人|同学|简历|推荐)?\s*([\u4e00-\u9fa5]{2,4})(?:，|\s|,)", cleaned)
    if match:
        name = match.group(1)
        if name not in {"今天", "明天", "周三", "周四", "周五", "简历", "面试"}:
            return name
    return None


def extract_position_name(text: str) -> str | None:
    normalized = text.replace(" ", "")
    for keyword in POSITION_KEYWORDS:
        if keyword.replace(" ", "") in normalized:
            return keyword.replace(" ", "")

    match = re.search(r"([\u4e00-\u9fa5A-Za-z]+(?:后端|前端|产品|测试|算法|运营|设计|开发|工程师|经理))", normalized)
    return match.group(1) if match else None


def extract_work_years(text: str) -> int | None:
    match = re.search(r"(\d+)\s*年(?:经验|工作经验|以上)?", text)
    return int(match.group(1)) if match else None


def extract_education(text: str) -> str | None:
    for keyword in EDUCATION_KEYWORDS:
        if keyword in text:
            return keyword
    return None


def extract_stage(text: str) -> str | None:
    for keyword in STAGE_KEYWORDS:
        if keyword in text:
            if keyword == "简历已收" and "初面" in text:
                return "初面"
            return keyword
    return None


def extract_interview_time(text: str) -> str | None:
    match = re.search(r"((?:今天|明天|后天|周[一二三四五六日天]|\d{1,2}[月/-]\d{1,2}[日号]?)\s*\d{1,2}[:：]\d{2})", text)
    if match:
        return match.group(1).replace(" ", "")
    match = re.search(r"(周[一二三四五六日天]\s*(?:上午|下午|晚上)?\s*\d{1,2}点)", text)
    return match.group(1).replace(" ", "") if match else None


def extract_interviewer(text: str) -> str | None:
    match = re.search(r"面试官[:：]?\s*([\u4e00-\u9fa5A-Za-z]{2,8})", text)
    if match:
        return match.group(1)
    match = re.search(r"([\u4e00-\u9fa5]{1,4}(?:经理|主管|总监|老师))", text)
    return match.group(1) if match else None


def extract_owner(text: str) -> str | None:
    match = re.search(r"负责人[:：]?\s*([\u4e00-\u9fa5A-Za-z]{2,8})", text)
    return match.group(1) if match else None
