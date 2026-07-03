

"""
流程：
1.根据recording_id查录音
2.检验录音是否可以用来生成摘要  是否被转写  转写状态，文本
3.查关联简历
4.查岗位信息，如果存在的话
5.预处理，涉及到文本是否需要分块
6.调Qwen结构化输出
7.把结果存到interview_summary
8.返回SummaryGenerateResponse
"""
import json

from fastapi import HTTPException
from langchain_core.outputs import llm_result
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from starlette import status


from app.crud.recordings import get_recording_by_id
from app.config import settings
from app.crud.position import get_position_by_id
from app.crud.resume import get_resume_by_id

from app.models import InterviewSummary
from app.prompt.summary_prompt import SUMMARY_PROMPT
from app.schemas.summary import SummaryGenerateRequest, InterviewSummaryLLMResult, SummaryGenerateResponse, \
    ChunkSummaryResult
from app.crud.summary import get_summary_by_recording_id
from prompt.summary_chunk_prompt import SUMMARY_CHUNK_PROMPT
from prompt.summary_consolidate_prompt import SUMMARY_CONSOLIDATE_PROMPT


#分两个链路，一个短的直接走，一个长的，拆分合并后一块走
def generate_summary(recording_id:int,db:Session):
    #1.查录音
    db_recording=get_recording_by_id(recording_id,db)
    if not db_recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该录音不存在")
    #2.检验转写状态
    if db_recording.transcript_status!=2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="录音尚未完成转写，不能生成摘要")
    if not db_recording.transcript:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="录音文字稿为空，不能生成摘要")
    #3.查简历
    db_resume=get_resume_by_id(db,db_recording.resume_id)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该简历不存在")
    #4.看下是否存在岗位信息
    db_position=None
    if db_recording.position_id is not None:
        db_position=get_position_by_id(db_recording.position_id,db)

    #5.预处理transcript
    transcript=preprocess_transcript(db_recording.transcript)

    #5.1 判断是否需要分块
    if len(transcript)>=6000:
        chunks=split_transcript(transcript)

        chunk_summaries=[]
        for chunk in chunks:
            chunk_result=extract_chunk_summary(chunk=chunk,
                                               candidate_name=db_resume.candidate_name or "",
                                               position_name=db_position.position_name if db_position else "",
                                               duration=build_duration_minutes(db_recording.duration)
                                               )
            chunk_summaries.append(chunk_result)

        #全部分块汇总完毕之后就开始处理，结构化、调用大模型
        llm_result=consolidate_summaries(
            chunk_summaries=chunk_summaries,
            candidate_name=db_resume.candidate_name or "",
            position_name=db_position.position_name if db_position else "",
            duration=build_duration_minutes(db_recording.duration)
        )
    else:#这里就是不需要分块
        # 6.构造prompt
        prompt = SUMMARY_PROMPT.format(
            candidate_name=db_resume.candidate_name or "",
            position_name=db_position.position_name if db_position else "",
            duration=build_duration_minutes(db_recording.duration),
            transcript=transcript
        )

        # 7.调用LLM
        llm = ChatOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL,
            model=settings.QWEN_MODEL
        )
        # 让模型带有结构的输出
        structured_llm = llm.with_structured_output(InterviewSummaryLLMResult)
        llm_result = structured_llm.invoke(prompt)
        llm_result = InterviewSummaryLLMResult.model_validate(llm_result)  # 现在的llm_result就是Interview。。这个类了，pydantic

    #8.查是否已经存在面试摘要
    db_summary=get_summary_by_recording_id(recording_id,db)
    if not db_summary:
        db_summary=InterviewSummary(
            recording_id=db_recording.id,
            resume_id=db_resume.id
        )
        db.add(db_summary)
    #无论是否存在面试摘要，我们都要将摘要放入，之前存在就覆盖
    #9.回填数据库其他字段，llm得到的结构化pydantic类
    db_summary.summary_overview=llm_result.summary_overview
    db_summary.key_qa=json.dumps( #json.dumps(...,ensure_ascii=False)  将python对象转为json字符串 表示的是中文不用acsii编码
        [item.model_dump() for item in llm_result.key_qa],#以json格式放入，本质还是字符串
        ensure_ascii=False
    )
    db_summary.technical_skills = json.dumps(llm_result.technical_skills, ensure_ascii=False)
    db_summary.soft_skills = json.dumps(llm_result.soft_skills, ensure_ascii=False)
    db_summary.highlights = json.dumps(llm_result.highlights, ensure_ascii=False)
    db_summary.concerns = json.dumps(llm_result.concerns, ensure_ascii=False)
    db_summary.candidate_questions = json.dumps(llm_result.candidate_questions, ensure_ascii=False)

    db.commit()
    db.refresh(db_summary)

    #10.返回响应
    return SummaryGenerateResponse(
        id=db_summary.id,
        recording_id=db_summary.recording_id,
        resume_id=db_summary.resume_id,
        summary_overview=llm_result.summary_overview,
        key_qa=llm_result.key_qa,
        technical_skills=llm_result.technical_skills,
        soft_skills=llm_result.soft_skills,
        highlights=llm_result.highlights,
        concerns=llm_result.concerns,
        candidate_questions=llm_result.candidate_questions
    )

#对文字稿进行预处理，数据清洗
def preprocess_transcript(transcript:str):
    if not transcript:
        return ""
    #transcript.splitlines()将换行符转为列表  if line.strip()过滤掉空行，如果拆了之后是空的就过滤 开头的line.strip()去掉每行首尾空格
    lines=[line.strip() for line in transcript.splitlines() if line.strip()]
    #转化为字符串，列表中的每个元素换行展示
    return "\n".join(lines)

#构建所需分钟用duration
def build_duration_minutes(duration_seconds:int |None):
    if not duration_seconds:
        return 0
    return max(1,round(duration_seconds/60))

#长文本的切分
def split_transcript(transcript:str):
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
        separators=["\n\n","\n","。",",","!",";"]
    )
    return text_splitter.split_text(transcript)


#分块的提炼--职责：输入一个chunk文本，调一次llm，返回ChunkSummaryResult
def extract_chunk_summary(chunk:str,candidate_name:str,position_name:str,duration:int):
    prompt=SUMMARY_CHUNK_PROMPT.format(
        candidate_name=candidate_name or "",
        position_name=position_name or "",
        duration =duration or 0,
        chunk_text=chunk
    )
    llm=ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL,
        temperature=0
    )
    structured_llm=llm.with_structured_output(InterviewSummaryLLMResult)
    result=structured_llm.invoke(prompt)

    return InterviewSummaryLLMResult.model_validate(result)

#为了更好的汇总，可以将前面得到的chunk结果转为文本
def build_chunk_summaries_text(chunk_summaries:list[InterviewSummaryLLMResult]):
    parts=[]

    #enumerate这个是让我们的循环每一次都带上索引，从start开始，不写start就是0
    for index,item in enumerate(chunk_summaries,start=1):
        parts.append(f"【片段摘要{index}】")
        parts.append(f"片段概述：{item.summary_overview}")

        parts.append("核心问答：")
        for qa in item.key_qa:
            parts.append(
                f"- 问题：{qa.question}；回答概述：{qa.answer_summary}；回答质量：{qa.answer_quality}"
            )
        parts.append(f"技术标签：{'、'.join(item.technical_skills)}")
        parts.append(f"软技能标签：{'、'.join(item.soft_skills)}")
        parts.append(f"亮点：{'；'.join(item.highlights)}")
        parts.append(f"疑虑点：{'；'.join(item.concerns)}")
        parts.append(f"候选人提问：{'；'.join(item.candidate_questions)}")
        parts.append("")

    #本身传入的是每个chunk的llm处理结果，放在一起，循环这种结构，字符串格式换行输出返回
    return "\n".join(parts)


#汇总所有的分块结果
def consolidate_summaries(chunk_summaries:list[InterviewSummaryLLMResult],candidate_name:str,position_name:str,duration:str):
    #这一步是将原来的pydantic结果转化为str类型的，方便传递给大模型作为文本提示词
    chunk_summaries_text=build_chunk_summaries_text(chunk_summaries)

    prompt=SUMMARY_CONSOLIDATE_PROMPT.format(
        candidate_name=candidate_name or "",
        position_name=position_name or "",
        duration=duration or 0,
        chunk_summaries_text=chunk_summaries_text
    )

    llm=ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL,
        temperature=0
    )
    structured_llm=llm.with_structured_output(InterviewSummaryLLMResult)

    result=structured_llm.invoke(prompt)

    return InterviewSummaryLLMResult.model_validate(result)


