EVALUATION_GENERATE_PROMPT="""
你是一位资深的HR评估专家，请根据以下面试摘要对候选人进行多维度评价。

【基本信息】
候选人：{candidate_name}
应聘岗位：{position_name}
岗位要求：{requirements}

【面试摘要】
面试概要：{summary_overview}

核心问答表现：
{key_qa_text}

能力标签：
- 技术能力：{technical_skills}
- 软技能：{soft_skills}

亮点：{highlights}
疑虑：{concerns}

请按以下JSON格式返回评价结果：
{{
    "scores": {{
        "professional": {{
            "score": 85,
            "comment": "对这个维度的具体评价（50字以内）"
        }},
        "logic": {{
            "score": 90,
            "comment": "..."
        }},
        "communication": {{
            "score": 80,
            "comment": "..."
        }},
        "learning": {{
            "score": 88,
            "comment": "..."
        }},
        "teamwork": {{
            "score": 82,
            "comment": "..."
        }},
        "culture_fit": {{
            "score": 78,
            "comment": "..."
        }}
    }},
    "total_score": 84.7,
    "recommendation": "推荐",
    "overall_comment": "综合评语（200-300字，包含优势、不足、发展建议）",
    "key_strengths": ["核心优势1", "核心优势2"],
    "improvement_areas": ["待提升领域1", "待提升领域2"],
    "hiring_suggestion": "录用建议和理由（100字）"
}}

评分标准：
- 90-100：表现优秀，明显超出期望
- 75-89：表现良好，符合期望
- 60-74：表现一般，勉强达到要求
- 0-59：表现较差，未达到要求

注意事项：
综合得分是按照其他维度的得分和权重计算的
professional:0.3
logic:0.2
communication:0.15
learning:0.15
teamwork:0.10
culture_fit:0.10

请基于面试表现客观评分，不要过于宽松或苛刻。
"""