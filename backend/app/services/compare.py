import tempfile
from pathlib import Path

from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from sqlalchemy.orm import Session
from starlette import status

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.crud.compare import get_compare
from app.config import settings
from app.prompt.compare_prompt import COMPARE_PROMPT
from app.schemas.compare import ComparisonAnalysisLLMResult, ComparisonAnalysisResponse


def ai_compare_analysis(id:int,db:Session):
    #1.查comparison
    db_compare=get_compare(id,db)
    if not db_compare:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="此对比不存在")

    #2.取comparison_data
    comparison_data=db_compare.comparison_data
    if not comparison_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="对比快照不存在")
    position = comparison_data.get("position") or {}
    candidates = comparison_data.get("candidates") or []

    if len(candidates)<2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="至少需要两个候选人")
    #3.动态拼接候选人文本
    candidates_text=build_candidates_prompt_text(candidates)

    #4.构造prompt
    prompt=COMPARE_PROMPT.format(
        position_name=position.get("name",""),
        candidates_text=candidates_text
    )

    #5.调LLM
    llm=ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL,
        temperature=0
    )
    structured_llm=llm.with_structured_output(ComparisonAnalysisLLMResult)
    llm_result=structured_llm.invoke(prompt)
    llm_result=ComparisonAnalysisLLMResult.model_validate(llm_result)

    #6.保存到数据库
    #数据库中的字段就是我们prompt中得到的
    db_compare.ai_analysis={
        "comparison_summary":llm_result.comparison_summary,
        #一直用model_dump是因为我们这里是pydantic对象（存放的是dict），不能直接json放入数据库，
        # 如果是普通dict就不用model_dump，直接赋值
        "candidate_analysis":[item.model_dump() for item in llm_result.candidate_analysis],
        "recommendation":llm_result.recommendation.model_dump(),
        "hiring_advice":llm_result.hiring_advice
    }
    db_compare.ranking=[item.model_dump() for item in llm_result.ranking]
    db.commit()
    db.refresh(db_compare)

    #7.返回
    return ComparisonAnalysisResponse(
        id=db_compare.id,
        comparison_summary=llm_result.comparison_summary,
        candidate_analysis=llm_result.candidate_analysis,
        ranking=llm_result.ranking,
        recommendation=llm_result.recommendation,
        hiring_advice=llm_result.hiring_advice
    )


#因为候选人的数量不定，所以我们需要动态拼接给llm的prompt
def build_candidates_prompt_text(candidates:list[dict]):
    parts=[]

    for index,item in enumerate(candidates,start=1):
        evaluation=item.get("evaluation") or {}
        skills=item.get("skills") or []

        parts.append(f"候选人{index} - {item.get('name', '')}：")
        parts.append(f"- 学历：{item.get('education', '')} - {item.get('school', '')}")
        parts.append(f"- 工作年限：{item.get('work_years', 0)}年")
        parts.append(f"- 当前职位：{item.get('current_position', '')}")
        parts.append(f"- 技能：{'、'.join(skills)}")
        parts.append(
            f"- 面试评分："
            f"专业{evaluation.get('professional_score', 0)}分、"
            f"逻辑{evaluation.get('logic_score', 0)}分、"
            f"沟通{evaluation.get('communication_score', 0)}分、"
            f"学习{evaluation.get('learning_score', 0)}分、"
            f"团队{evaluation.get('teamwork_score', 0)}分、"
            f"文化{evaluation.get('culture_score', 0)}分"
        )
        parts.append(f"- 综合得分：{evaluation.get('total_score', 0)}分")
        parts.append("")

    return "\n".join(parts)

#导出PDF对比分析报告 -- 根据id
def build_compare_report_pdf(compare_id:int,db:Session):
    #报告中要有candidate basic、score、ai，不强依赖ai分析结果

    #1.根据id查记录
    db_compare =get_compare(compare_id,db)
    if not db_compare:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="没有候选人对比记录")
    comparison_data=db_compare.comparison_data

    if not comparison_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="对比数据为空")

    ai_analysis=db_compare.ai_analysis
    ranking=db_compare.ranking

    position=comparison_data.get("position") or {}
    candidates=comparison_data.get("candidates") or []

    if not candidates:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="候选人数据为空")

    #存放下载pdf的路径，还没创建此文件夹
    temp_dir=tempfile.mkdtemp(prefix="compare_report_")
    pdf_path=str(Path(temp_dir)/f"candidate_comparison_{compare_id}.pdf")

    doc=SimpleDocTemplate(pdf_path,pagesize=A4)
    #得到一个标题层级，后面可以直接根据字段得到对应的大小
    pdfmetrics.registerFont(
        TTFont("MicrosoftYaHei", r"C:\Windows\Fonts\msyh.ttc")
    )

    styles = getSampleStyleSheet()
    styles["Title"].fontName = "MicrosoftYaHei"
    styles["Heading2"].fontName = "MicrosoftYaHei"
    styles["Heading3"].fontName = "MicrosoftYaHei"
    styles["Normal"].fontName = "MicrosoftYaHei"
    story=[]

    #1.标题
    story.append(Paragraph("候选人对比报告",styles["Title"]))
    story.append(Spacer(1,12))

    #2.岗位信息
    story.append(Paragraph(f"岗位名称：{position.get('name','')}",styles["Normal"]))
    story.append(Paragraph(f"对比人数:{len(candidates)}",styles["Normal"]))
    story.append(Paragraph(f"创建时间：{db_compare.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1,12))

    #3.基础信息表
    basic_table=build_candidate_basic_table(candidates)
    story.append(Paragraph("一、候选人基础信息对比",styles["Heading2"]))
    story.append(basic_table)
    story.append(Spacer(1,12))

    #4.评分对比表
    score_table=build_candidate_score_table(candidates)
    story.append(Paragraph("二、候选人评分对比",styles["Heading2"]))
    story.append(score_table)
    story.append(Spacer(1,12))

    #5.AI分析
    build_ai_analysis_section(story,ai_analysis,ranking,styles)

    doc.build(story)
    return pdf_path

#构建一些PDF需要的字段

#基础信息表
def build_candidate_basic_table(candidates:list[dict]):
    #data是列表包含列表
    data=[["姓名","学历","学校","工作年限","当前职位","技能"]]

    for item in candidates:
        #将skills变成str
        skills = format_skills_for_pdf(item.get("skills") or [])
        data.append([
            item.get("name", ""),
            item.get("education", ""),
            item.get("school", ""),
            str(item.get("work_years", "") or ""),
            item.get("current_position", ""),
            skills
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "MicrosoftYaHei")
    ]))
    return table

#让skills分行
def format_skills_for_pdf(skills: list[str], per_line: int = 3) -> str:
    if not skills:
        return ""

    lines = []
    for i in range(0, len(skills), per_line):
        line = "、".join(skills[i:i + per_line])
        lines.append(line)

    return "\n".join(lines)

#评分对比表
def build_candidate_score_table(candidates:list[dict]):
    data = [["姓名", "专业", "逻辑", "沟通", "学习", "团队", "文化", "综合分"]]

    for item in candidates:
        evaluation = item.get("evaluation") or {}
        data.append([
            item.get("name", ""),
            evaluation.get("professional_score", ""),
            evaluation.get("logic_score", ""),
            evaluation.get("communication_score", ""),
            evaluation.get("learning_score", ""),
            evaluation.get("teamwork_score", ""),
            evaluation.get("culture_score", ""),
            evaluation.get("total_score", "")
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "MicrosoftYaHei")
    ]))
    return table

#AI分析部分
def build_ai_analysis_section(story,ai_analysis:dict |None,ranking:list | None,styles):
    if not ai_analysis and not ranking:
        return

    story.append(Paragraph("三、AI 对比分析", styles["Heading2"]))

    if ai_analysis:
        summary = ai_analysis.get("comparison_summary", "")
        if summary:
            story.append(Paragraph(f"对比总结：{summary}", styles["Normal"]))
            story.append(Spacer(1, 8))

        candidate_analysis = ai_analysis.get("candidate_analysis") or []
        for item in candidate_analysis:
            story.append(Paragraph(f"候选人：{item.get('name', '')}", styles["Heading3"]))
            story.append(Paragraph(f"优势：{'；'.join(item.get('advantages_over_others') or [])}", styles["Normal"]))
            story.append(Paragraph(f"劣势：{'；'.join(item.get('disadvantages') or [])}", styles["Normal"]))
            story.append(Paragraph(f"适合场景：{item.get('suitable_scenarios', '')}", styles["Normal"]))
            story.append(Paragraph(f"风险点：{item.get('risk_points', '')}", styles["Normal"]))
            story.append(Spacer(1, 8))

        recommendation = ai_analysis.get("recommendation") or {}
        if recommendation:
            story.append(Paragraph("推荐结论", styles["Heading3"]))
            story.append(Paragraph(f"最佳人选：{recommendation.get('best_choice', '')}", styles["Normal"]))
            story.append(Paragraph(f"推荐理由：{recommendation.get('reason', '')}", styles["Normal"]))
            story.append(Paragraph(f"备选人选：{recommendation.get('alternative', '')}", styles["Normal"]))
            story.append(Paragraph(f"备选理由：{recommendation.get('alternative_reason', '')}", styles["Normal"]))
            story.append(Spacer(1, 8))

        hiring_advice = ai_analysis.get("hiring_advice", "")
        if hiring_advice:
            story.append(Paragraph("录用建议", styles["Heading3"]))
            story.append(Paragraph(hiring_advice, styles["Normal"]))
            story.append(Spacer(1, 8))

    if ranking:
        story.append(Paragraph("四、候选人排名", styles["Heading2"]))
        for item in ranking:
            story.append(
                Paragraph(
                    f"第{item.get('rank', '')}名：{item.get('name', '')}（{item.get('score', '')}分）- {item.get('reason', '')}",
                    styles["Normal"]
                )
            )