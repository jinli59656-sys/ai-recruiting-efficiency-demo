import math

from app.schemas.screnning import PositionMatchAnalysis

EDUCATION_LEVEL_MAP={
    "大专":1,
    "本科":2,
    "硕士":3,
    "博士":4
}

#学历过滤
def check_education(candidate_education:str|None,min_education:str|None):
    if not min_education:
        return True

    candidate_level=EDUCATION_LEVEL_MAP.get(candidate_education or "",0)
    required_level=EDUCATION_LEVEL_MAP.get(min_education,0)

    return candidate_level>=required_level

#技能过滤
def check_required_skills(candidate_skills:list[str] | None,required_skills:list[str] |None):
    if not required_skills:
        return True
    candidate_skill_set=set(candidate_skills or [])
    return all(skill in candidate_skill_set for skill in required_skills)

#构建匹配的分数
def build_match_score(similarity:float):
    score=int(round(similarity*100))
    if score<0:
        return 0
    if score>100:
        return 100
    return score

#构建推荐等级
def build_recommendation(match_score:int):
    if match_score>=85:
        return "强烈推荐"
    if match_score>=70:
        return "推荐"
    if match_score>=50:
        return "可考虑"

    return "不推荐"

#构建匹配分析（话） 需要llm去生成
def build_temp_match_analysis():
    return PositionMatchAnalysis(
        match_advantages=["待大模型生成"],
        match_weaknesses=["待大模型生成"],
        overall_comment="待大模型生成",
        interview_suggestions=["待大模型生成"]
    )

#计算余弦相似度
def consine_similarity(vec1:list[float],vec2:list[float]):
    if not vec1 or not vec2:
        return 0.0

    dot_product=sum(a * b for a,b in zip(vec1,vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)
