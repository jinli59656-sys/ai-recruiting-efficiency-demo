
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.crud.position import get_position_by_id
from app.crud.resume import get_resumes_by_ids, get_resume_by_id, batch_update_resume_status
from app.database import get_db
from app.schemas.resume import ResumePositionInfo
from app.schemas.screnning import PositionMatchRequest, CustomMatchRequest, PositionMatchInfo, PositionMatchResponse, \
    PositionMatchAnalysis, CustomMatchResponse, PositionAnalysisResponse, BatchMarkRequest
from app.services.resume_embedding import embed_resume_text, build_position_embedding_text
from app.services.screening import check_education, check_required_skills, build_match_score, build_recommendation, \
    build_temp_match_analysis, consine_similarity
from app.services.screening_llm import generate_match_analysis, generate_custom_analysis
from app.storage.milvus_storage import search_resume_embeddings, get_resume_embedding_by_resume_id
from app.utils.response import success_response

router=APIRouter(prefix="/api/v1/screening",tags=["智能简历筛选"])

@router.post("/match",summary="岗位匹配筛选")
def position_match(data:PositionMatchRequest,db:Session=Depends(get_db)):
    #1.先根据岗位id获取岗位的信息，取出JD，进行向量化
    db_position=get_position_by_id(data.position_id,db)
    if not db_position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="岗位不存在")
    text =build_position_embedding_text(db_position)
    query_vector=embed_resume_text(text)
    print("岗位向量文本====：",text)

    # 2.去Milvus检索
    hits=search_resume_embeddings(query_vector,data.top_n*5)
    print("milvus命中数量：",len(hits))
    resume_ids=[]
    score_map={}
    seen=set()
    # 3.从检索结果中取出得分、id
    for hit in hits:
        resume_id = int(hit.entity.get("resume_id"))
        score = float(hit.score)

        if resume_id not in score_map or score > score_map[resume_id]:
            score_map[resume_id] = score

        if resume_id not in seen:
            seen.add(resume_id)
            resume_ids.append(resume_id)
    # 4.查询id对应的简历
    db_resumes=get_resumes_by_ids(resume_ids,db)
    resume_map={item.id:item for item in db_resumes}
    # 5.针对得到的简历进行过滤，只保留需要的
    #过滤逻辑可以写在sevice层
    filtered_resumes=[]
    for resume_id in resume_ids:
        db_resume=resume_map.get(resume_id)
        if not db_resume:
            continue
        if not check_education(db_resume.education,data.min_education):
            continue
        if data.min_work_years is not None and (db_resume.work_years or 0)<data.min_work_years:
            continue
        if not check_required_skills(db_resume.skills,data.required_skills):
            continue
        filtered_resumes.append(db_resume)
    filtered_resumes=filtered_resumes[:data.top_n]
    print("过滤后简历数量：", len(filtered_resumes))
    #6.filtered_resumes里面都是最终需要的简历
    results=[]
    for item in filtered_resumes:
        similarity=round(float(score_map.get(item.id,0.0)),4)
        match_score=build_match_score(similarity)
        recommendation=build_recommendation(match_score)
        match_analysis=build_temp_match_analysis()
        position_match_info =PositionMatchInfo(
            resume_id=item.id,
            candidate_name=item.candidate_name,
            education=item.education or " ",
            work_years=item.work_years or 0,
            current_position=item.current_position or " ",
            match_score=match_score,
            similarity=similarity,
            recommendation=recommendation,
            match_analysis=None

            #每个resume都调太慢了，超时，这里先不返回ai匹配分析
            # match_analysis=generate_match_analysis(
            #     position_name=db_position.position_name,
            #     job_description=db_position.job_description,
            #     requirements=db_position.requirements,
            #     candidate_name=item.candidate_name or "",
            #     education=item.education or "",
            #     work_years=item.work_years or 0,
            #     current_position=item.current_position or "",
            #     skills=item.skills or [],
            #     work_experience=item.work_experience or " ",
            #     project_experience=item.project_experience or " ",
            #     resume_summary=item.resume_summary or " ",
            #     similarity=similarity,
            #     match_score=match_score,
            # )
        )
        results.append(position_match_info)


    position_new=ResumePositionInfo(
        id=data.position_id,
        name=db_position.position_name
    )
    total_matched=len(filtered_resumes)
    data=PositionMatchResponse(
        position=position_new,
        total_matched=total_matched,
        results=results
    )
    return success_response(message="Milvus检索成功",data=data)

#自定义筛选，就是给一段描述，你找到与描述相关的简历
@router.post("/custom",summary="自定义筛选")
def custom_position(data:CustomMatchRequest,db:Session=Depends(get_db)):
    #1.将query拿去向量化
    query_vector=embed_resume_text(data.query)
    # 2.拿着向量去进行相似度匹配 ，因为只有这一条语句的限定条件，所以不需要扩大召回数量
    hits=search_resume_embeddings(query_vector,data.top_n)
    # 3.之前创建embedding表的时候，定义的字段是resume_id,embedding,向量id
    # 3.1从hit中去一下score和简历id
    results=[]
    for hit in hits:
        resume_id=int(hit.entity.get("resume_id"))
        score=float(hit.score)
        similarity=round(score,4)
        db_resume=get_resume_by_id(db,resume_id)
        if not db_resume:
            continue
        match_score=build_match_score(score)
        # 4.得到了匹配的简历和分数，下面赋值
        position_match_info = PositionMatchInfo(
            resume_id=resume_id,
            candidate_name=db_resume.candidate_name or "",
            education=db_resume.education or "",
            work_years=db_resume.work_years or 0,
            current_position=db_resume.current_position or "",
            match_score=match_score,
            similarity=similarity,
            recommendation=build_recommendation(match_score),
            match_analysis=generate_custom_analysis(
                query=data.query,
                candidate_name=db_resume.candidate_name or "",
                education=db_resume.education or "",
                work_years=db_resume.work_years or 0,
                current_position=db_resume.current_position or "",
                skills=db_resume.skills or [],
                work_experience=db_resume.work_experience or " ",
                project_experience=db_resume.project_experience or " ",
                resume_summary=db_resume.resume_summary or " ",
                similarity=similarity,
                match_score=match_score,
            )
        )
        results.append(position_match_info)
    data=CustomMatchResponse(query=data.query,total_matched=len(hits),results=results)
    return success_response(message="自定义匹配成功",data=data)



#查询一份简历对一个岗位的匹配分析
@router.get("/analysis/{resume_id}",summary="获取匹配分析")
def get_analysis(resume_id:int,position_id:int,db:Session=Depends(get_db)):
    #1.根据岗位和简历id得到岗位和候选人，再放入prompt，让llm生成分析
    db_resume=get_resume_by_id(db,resume_id)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该简历不存在")
    db_position=get_position_by_id(position_id,db)
    if not db_position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该岗位不存在")

    #2.将position的字段拿去向量化
    text =build_position_embedding_text(db_position)
    query_vector=embed_resume_text(text)

    # 3.查找该简历的向量
    resume_vector_data=get_resume_embedding_by_resume_id(resume_id)
    if not resume_vector_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该简历没有向量数据")
    #3.1 取出刚刚的简历向量中的向量
    resume_vector = resume_vector_data["embedding"]

    # 4.对这两个向量进行相似度匹配，得到分数
    similarity=consine_similarity(query_vector,resume_vector)
    match_score=build_match_score(similarity)
    if not db_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="该简历不存在")
    #构建返回结果的分析结果
    result =generate_match_analysis(db_position.position_name,db_position.job_description,
                            db_position.requirements,db_resume.candidate_name,
                            db_resume.education,db_resume.work_years,db_resume.current_position,
                            db_resume.skills,db_resume.work_experience,db_resume.project_experience,
                            db_resume.resume_summary,similarity=similarity,match_score=match_score)
    data=PositionAnalysisResponse(position_id=position_id,resume_id=resume_id,similarity=similarity,result=result)
    return success_response(message="获取匹配分析结果成功",data=data)

@router.post("/batch-mark",summary="批量标记")
def batch_mark(data:BatchMarkRequest,db:Session=Depends(get_db)):
    #根据传入的ids，修改状态
    count=batch_update_resume_status(data.resume_ids,data.mark,db)
    db.flush()
    db.commit()
    return success_response(message=f"批量修改{count}条简历")

