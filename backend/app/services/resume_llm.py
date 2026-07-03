#这个类只负责拼prompt、调模型、把模型结果转为ResumeParseResult --也就是我们定义的pydantic

from langchain_openai import ChatOpenAI

from app.config import settings
from app.prompt.resume_parse_prompt import RESUME_PARSE_PROMPT
from app.schemas.resume_parse import ResumeParseResult


def extract_resume_structured_data(resume_text:str)->ResumeParseResult:
    prompt=RESUME_PARSE_PROMPT.format(resume_text=resume_text)

    llm=ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL,
        temperature=0,
    )
    #让大模型带有格式的输出
    structured_llm=llm.with_structured_output(ResumeParseResult)
    result=structured_llm.invoke(prompt)
    return ResumeParseResult.model_validate(result)
