import json

from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.question import create_question
from app.models import Resume, JobPosition
from app.prompt.question_generate_prompt import QUESTION_GENERATE_PROMPT
from app.schemas.question import QuestionCreateRequest, QuestionItem, QuestionLLMResult, QuestionItemResponse, \
    QuestionCreateResponse


#生成面试题，返回的格式是后端返回给前端的数据格式
def generate_questions_and_save(data:QuestionCreateRequest,db_position,db_resume,db:Session):
    #1.组装prompt
    prompt=build_question_prompt(data=data,db_position=db_position,db_resume=db_resume)

    # 2.调用llm
    llm=ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL,
        temperature=0
    )

    structured_llm=llm.with_structured_output(QuestionLLMResult)
    llm_result =structured_llm.invoke(prompt)
    llm_result=QuestionLLMResult.model_validate(llm_result)

    saved_questions=[]

    for item in llm_result.questions:
        # 3.把题目保存到数据库
        db_question=create_question(data.position_id,data.resume_id,build_question_types_code(item.type),build_difficulty_text_code(item.difficulty),
                                    item.question,item.reference_answer,json.dumps(item.scoring_points,ensure_ascii=False),
                                    item.source,db)

        saved_questions.append(
            QuestionItemResponse(
                id=db_question.id,
                is_saved=db_question.is_saved,
                **item.model_dump()
            )
        )
    db.commit()

    # 4.组装最终响应
    return QuestionCreateResponse(
        mode=data.mode,
        position_id=data.position_id,
        resume_id=data.resume_id,
        count=len(saved_questions),
        questions=saved_questions
    )


def build_question_prompt(data:QuestionCreateRequest,db_position,db_resume):
    prompt=QUESTION_GENERATE_PROMPT.format(
        position_name=db_position.position_name if db_position else "",
        job_description=db_position.job_description if db_position else "",
        requirements=db_position.requirements if db_position else "",
        candidate_name=db_resume.candidate_name if db_resume else "",
        education=db_resume.education if db_resume else "",
        school=db_resume.school if db_resume else "",major=db_resume.major if db_resume else "",
        work_years=db_resume.work_years if db_resume else 0,
        current_position=db_resume.current_position if db_resume else "",
        current_company=db_resume.current_company if db_resume else "",
        skills=build_skills_text(db_resume.skills if db_resume else None), #转化为自然文本
        work_experience_summary=build_work_experience_text(db_resume.work_experience if db_resume else None),
        project_experience_summary=build_project_experience_text(db_resume.project_experience if db_resume else None),
        question_types=build_question_types(data.question_types) or "",
        difficulty=build_difficulty_text(data.difficulty) or "",
        count=data.count or 0,
        with_answer="是" if data.with_answer else "否"
    )
    return prompt


def build_work_experience_text(work_experiences):
    if not work_experiences:
        return ""

    lines = []
    for item in work_experiences:
        company = item.get("company", "")
        position = item.get("position", "")
        description = item.get("description", "")
        lines.append(f"公司：{company}，岗位：{position}，职责：{description}")

    return "\n".join(lines)


def build_project_experience_text(project_experiences):
    if not project_experiences:
        return ""

    lines = []
    for item in project_experiences:
        project_name = item.get("project_name", "")
        role = item.get("role", "")
        description = item.get("description", "")
        lines.append(f"项目：{project_name}，角色：{role}，描述：{description}")

    return "\n".join(lines)

def build_skills_text(skills):
    if not skills:
        return ""
    return "、".join(skills)

def build_question_types(types:list[str]):
    type_map={
        "technical":"技术类",
        "behavioral":"行为类",
        "situational":"情景类",
        "open":"开放类"
    }
    return "、".join(type_map[item] for item in types)

def build_question_types_code(type:str):
    type_map={
        "技术类":"technical",
        "行为类":"behavioral",
        "情景类":"situational",
        "开放类":"open"
    }
    return type_map[type]

def build_difficulty_text(difficulty):
    difficulty_map={
        "junior":"初级",
        "middle":"中级",
        "senior":"高级"
    }
    return difficulty_map[difficulty]

def build_difficulty_text_code(difficulty):
    difficulty_map={
        "初级":"junior",
        "中级":"middle",
        "高级":"senior"
    }
    return difficulty_map[difficulty]
