RESUME_PARSE_PROMPT = """
  请从以下简历文本中提取结构化信息，并以 JSON 格式返回。

  简历内容：
  {resume_text}

  请严格按照以下 JSON 格式返回：
  {{
      "candidate_name": "姓名",
      "phone": "手机号",
      "email": "邮箱",
      "education": "最高学历(博士/硕士/本科/大专)",
      "school": "毕业院校",
      "major": "专业",
      "work_years": 工作年限数字,
      "current_company": "当前公司",
      "current_position": "当前职位",
      "skills": ["技能1", "技能2"],
      "work_experience": [
          {{
              "company": "公司名",
              "position": "职位",
              "start_date": "开始时间",
              "end_date": "结束时间",
              "description": "工作描述"
          }}
      ],
      "project_experience": [
          {{
              "project_name": "项目名称",
              "role": "担任角色",
              "description": "项目描述"
          }}
      ],
      "education_experience": [
          {{
              "school": "学校",
              "major": "专业",
              "degree": "学历",
              "start_date": "开始时间",
              "end_date": "结束时间"
          }}
      ],
      "resume_summary": "用50字概括该候选人的核心优势"
  }}

  要求：
  1. 如果某字段无法提取，请填写 null。
  2. 如果某个列表字段无法提取，请返回空列表 [] 或 null，保持 JSON 合法。
  3. 只返回 JSON，不要返回解释说明，不要使用 Markdown 代码块。
  4. work_years 必须返回数字，如果无法判断则返回 null。
  """