SUMMARY_CONSOLIDATE_PROMPT = """
  你是一位专业的HR助手，请根据以下多个面试片段摘要，整合生成最终的结构化面试摘要。

  注意：
  1. 以下内容来自同一场面试的不同片段摘要，存在重复信息。
  2. 请去重、合并、归纳，生成最终统一结果。
  3. 不要机械拼接各片段内容，要形成一份完整、简洁、专业的最终摘要。
  4. 如果某项信息不明确，不要编造。

  【面试信息】
  候选人：{candidate_name}
  应聘岗位：{position_name}
  面试时长：{duration}分钟

  【片段摘要集合】
  {chunk_summaries_text}

  请严格按以下JSON格式返回：
  {{
      "summary_overview": "面试整体概述（150-200字）",
      "key_qa": [
          {{
              "question": "面试官提出的重要问题",
              "answer_summary": "候选人回答要点概述（100字以内）",
              "answer_quality": "优秀/良好/一般/较差"
          }}
      ],
      "technical_skills": ["技术能力标签1", "技术能力标签2"],
      "soft_skills": ["软技能标签1", "软技能标签2"],
      "highlights": ["亮点1", "亮点2"],
      "concerns": ["疑虑1", "疑虑2"],
      "candidate_questions": ["候选人提出的问题1", "候选人提出的问题2"]
  }}

  要求：
  1. key_qa 只保留最重要的3-5组，去除重复和相似问题。
  2. technical_skills 保留3-8个最关键标签，去重。
  3. soft_skills 保留3-6个最关键标签，去重。
  4. highlights 保留2-4条，concerns 保留2-3条。
  5. candidate_questions 只保留候选人明确提出的问题，去重。
  6. 只返回合法JSON，不要返回解释文字或Markdown代码块。
  """