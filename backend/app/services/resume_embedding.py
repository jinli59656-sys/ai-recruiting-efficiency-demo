from typing import Any, List

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import settings
from app.models import JobPosition, Resume


def build_resume_embedding_text(resume:Resume)->str:
    """
    将简历中的关键内容拼接成一段用与向量化的文本
    当前需要拼接：
    1.原始简历文本：original_content
    2.技能标签：skills
    3.工作经验：work_experience
    4.项目经验：project_experience
    """

    original_content=(resume.original_content or "").strip()
    skill_text=format_skills(resume.skills)
    work_experience=format_work_experience(resume.work_experience)
    project_experience=format_project_experience(resume.project_experience)

    parts=[
        "简历原文:",
        original_content or "无",
        "",
        "技能标签:",
        skill_text or "无",
        "",
        "工作经历:",
        work_experience or "无",
        "",
        "项目经历:",
        project_experience or "无",
    ]

    return "\n".join(str(part) for part in parts).strip()

#拼接智能筛选简历的文本
def build_position_embedding_text(position:JobPosition):
    return "\n".join([
        f"岗位名称：{position.position_name or ''}",
        f"岗位职责：{position.job_description or ''} ",
        f"任职要求：{position.requirements or ''}"
    ]).strip()


#创建向量
def embed_resume_text(text:str)->list[float]:
    if text is None:
        raise ValueError("向量化文本不能为空")

    if not isinstance(text, str):
        text = str(text)

    text = text.strip()
    if not text:
        raise ValueError("向量化文本不能为空字符串")
    embedding_model=OpenAIEmbeddings(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_EMBEDDING_MODEL,
        dimensions=settings.QWEN_EMBEDDING_DIMENSIONS,
        #加下面两个参数是因为，直接把text给langchain，langchain内部处理的结果不兼容
        check_embedding_ctx_length=False,
        tiktoken_enabled=False
    )
    return embedding_model.embed_query(text)  #两个方法可以传入字符串或者字符串数组


def format_skills(skills:list[str]|None)-> str:
    if not skills:
        return ""
    return "、".join(skill.strip() for skill in skills if skill and skill.strip())

def format_work_experience(work_experience:list[dict]|None)->str:
    if not work_experience:
        return ""

    lines=[]
    for item in work_experience:
        company = (item.get("company") or "").strip()
        position = (item.get("position") or "").strip()
        start_date = (item.get("start_date") or "").strip()
        end_date = (item.get("end_date") or "").strip()
        description = (item.get("description") or "").strip()

        line_parts=[]
        if company:
            line_parts.append(f"公司：{company}")
        if position:
            line_parts.append(f"职位：{position}")
        if start_date or end_date:
            line_parts.append(f"时间：{start_date} - {end_date}".strip(" -"))
        if description:
            line_parts.append(f"描述：{description}")

        if line_parts:
            lines.append("；".join(line_parts))

    return "\n".join(lines)


def format_project_experience(project_experience: list[dict] | None) -> str:
    if not project_experience:
        return ""

    lines = []
    for item in project_experience:
        project_name = (item.get("project_name") or "").strip()
        role = (item.get("role") or "").strip()
        description = (item.get("description") or "").strip()

        line_parts = []
        if project_name:
            line_parts.append(f"项目：{project_name}")
        if role:
            line_parts.append(f"角色：{role}")
        if description:
            line_parts.append(f"描述：{description}")

        if line_parts:
            lines.append("；".join(line_parts))

    return "\n".join(lines)
