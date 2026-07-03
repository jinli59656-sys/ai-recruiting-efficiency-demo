
SUMMARY_CHUNK_PROMPT="""
你是一位专业的HR助手，请从以下面试记录片段中提取局部关键信息。

  【面试信息】
  候选人：{candidate_name}
  应聘岗位：{position_name}
  面试时长：{duration}分钟

  【面试记录片段】
  {chunk_text}

  请严格按以下JSON格式返回：
  {{
      "chunk_overview": "该片段的简要概述（80-120字）",
      "key_qa": [
          {{
              "question": "片段中明确出现的重要问题",
              "answer_summary": "候选人回答要点概述（100字以内）",
              "answer_quality": "优秀/良好/一般/较差"
          }}
      ],
      "technical_skills": ["技术标签1", "技术标签2"],
      "soft_skills": ["软技能标签1", "软技能标签2"],
      "highlights": ["亮点1", "亮点2"],
      "concerns": ["疑虑1", "疑虑2"],
      "candidate_questions": ["候选人提问1", "候选人提问2"]
  }}

  要求：
  1. 只基于当前片段提取，不要推断整场面试结论。
  2. key_qa 只提取当前片段中最明确的问答，数量1-3个即可。
  3. technical_skills 和 soft_skills 只提取当前片段中明确体现的内容。
  4. candidate_questions 只有在能明确判断是候选人提出时才返回，否则返回空数组 []。
  5. 如果某项无法明确提取，请返回空数组或保守概括，不要编造。
  6. 只返回合法JSON，不要返回解释文字或Markdown代码块。
"""