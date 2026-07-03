
QUESTION_GENERATE_PROMPT="""
你是一位资深的技术面试官，请根据以下信息生成面试题目。

【目标岗位】
岗位名称：{position_name}
岗位职责：
{job_description}

任职要求：
{requirements}

【候选人信息】
姓名：{candidate_name}
学历：{education} - {school} - {major}
工作年限：{work_years}年
当前职位：{current_position} @ {current_company}
技能标签：{skills}
工作经历摘要：{work_experience_summary}
项目经验摘要：{project_experience_summary}

【生成要求】
- 题目类型：{question_types}（可多选：技术类/行为类/情景类/开放类）
- 难度等级：{difficulty}（初级/中级/高级）
- 题目数量：{count}题
- 是否生成参考答案：{with_answer}

请按以下JSON格式返回：
{{
    "questions": [
        {{
            "type": "技术类",
            "difficulty": "中级",
            "question": "题目内容",
            "reference_answer": "参考答案（如需要）",
            "scoring_points": ["评分要点1", "评分要点2"],
            "source": "基于岗位要求/基于候选人经历"
        }}
    ]
}}

要求：
1. 技术类题目要结合岗位技术栈和候选人技能
2. 行为类题目要基于候选人的工作经历设计
3. 题目要有区分度，能考察真实能力
4. 参考答案要给出关键点，不要过于冗长
"""