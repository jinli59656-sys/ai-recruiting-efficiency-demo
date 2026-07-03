from langchain_openai import ChatOpenAI

from app.config import settings
from app.prompt.position_custom_prompt import POSITION_MATCH_PROMPT1
from app.prompt.position_match_prompt import POSITION_MATCH_PROMPT
from app.schemas.screnning import PositionMatchAnalysis


#写一个生成分析的服务函数
def generate_match_analysis(
    position_name: str,
    job_description: str,
    requirements: str,
    candidate_name: str,
    education: str,
    work_years: int,
    current_position: str,
    skills: list[str] | None,
    work_experience,
    project_experience,
    resume_summary: str | None,
    similarity: float,
    match_score: int,
):
    prompt=POSITION_MATCH_PROMPT.format(
        position_name=position_name or "",
        job_description=job_description or "",
        requirements=requirements or "",
        candidate_name=candidate_name or "",
        education=education or "",
        work_years=work_years or 0,
        current_position=current_position or "",
        skills="、".join(skills or []),
        work_experience=str(work_experience or []),
        project_experience=str(project_experience or []),
        resume_summary=resume_summary or "",
        similarity=similarity,
        match_score=match_score,
    )

    llm=ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL,
        temperature=0
    )
    structuerd_llm=llm.with_structured_output(PositionMatchAnalysis)
    result=structuerd_llm.invoke(prompt)
    return PositionMatchAnalysis.model_validate(result)

#写一个生成分析的服务函数
def generate_custom_analysis(
    query:str,
    candidate_name: str,
    education: str,
    work_years: int,
    current_position: str,
    skills: list[str] | None,
    work_experience,
    project_experience,
    resume_summary: str | None,
    similarity: float,
    match_score: int,
):
    prompt=POSITION_MATCH_PROMPT1.format(
        query=query or "",
        candidate_name=candidate_name or "",
        education=education or "",
        work_years=work_years or 0,
        current_position=current_position or "",
        skills="、".join(skills or []),
        work_experience=str(work_experience or []),
        project_experience=str(project_experience or []),
        resume_summary=resume_summary or "",
        similarity=similarity,
        match_score=match_score,
    )

    llm=ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL,
        temperature=0
    )
    structuerd_llm=llm.with_structured_output(PositionMatchAnalysis)
    result=structuerd_llm.invoke(prompt)
    return PositionMatchAnalysis.model_validate(result)
