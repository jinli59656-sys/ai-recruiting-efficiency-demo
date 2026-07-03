COMPARE_PROMPT="""
你是一位资深的招聘顾问，请对以下候选人进行对比分析。

【目标岗位】
岗位名称：{position_name}

【候选人信息】
{candidates_text}


请按以下JSON格式返回对比分析（在你生成的时候注意这个模板中的分数满分都是100分）：
{{
    "comparison_summary": "对比总结（200字，概述各候选人的整体情况和差异）",

    "candidate_analysis": [
        {{
            "name": "候选人姓名",
            "advantages_over_others": ["相比其他候选人的优势1", "优势2"],
            "disadvantages": ["相比其他候选人的劣势1"],
            "suitable_scenarios": "最适合的场景（如急需上岗、长期培养等）",
            "risk_points": "录用风险点"
        }}
    ],

    "ranking": [
        {{
            "rank": 1,
            "name": "候选人姓名",
            "score": 综合推荐分,
            "reason": "排名第一的理由（50字）"
        }}
    ],

    "recommendation": {{
        "best_choice": "最佳人选姓名",
        "reason": "推荐理由（100字）",
        "alternative": "备选人选姓名",
        "alternative_reason": "备选理由"
    }},

    "hiring_advice": "最终录用建议（150字，包含决策建议和注意事项）"
}}

分析要求：
1. 客观公正，基于数据和面试表现
2. 突出每个候选人的差异化优势
3. 考虑岗位需求的匹配度
4. 给出明确的排名和推荐
5.分数的总分均为100分
"""