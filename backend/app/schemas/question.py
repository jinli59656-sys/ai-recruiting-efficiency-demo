from typing import Literal, Optional

from docx import comments
from openai.resources.beta.threads.runs import steps
from pandas.core.computation import common
from pydantic import BaseModel, Field, ConfigDict

#枚举一下模式、类型、难度，这样方便前端传值
QuestionMode=Literal["position","resume","hybrid"]
QuestionType=Literal["technical","behavioral","situational","open"]
DifficultyLevel=Literal["junior","middle","senior"]

#面试题生成，前端传入的应该是模式、岗位、简历ID、类型、难度、题目数量，是否携带参考答案
class QuestionCreateRequest(BaseModel):
    mode:QuestionMode=Field(...,description="生成模式")
    position_id:int |None=Field(default=None,alias="positionId",description="岗位ID")
    resume_id:int | None=Field(default=None,alias="resumeId",description="简历ID")
    question_types:list[QuestionType]=Field(...,alias="questionTypes",min_length=1,description="题目类型列表")
    difficulty:DifficultyLevel=Field(...,description="题目难度")
    count:int=Field(...,ge=1,le=20,description="题目数量")
    with_answer:bool=Field(default=True,alias="withAnswer",description="是否返回参考答案")


#编辑题目请求体
class QuestionUpdateRequest(BaseModel):
    type:QuestionType |None=Field(default=None,description="题目类型")
    difficulty:DifficultyLevel|None=Field(default=None,description="题目难度")
    question:str|None=Field(default=None,description="题目内容")
    reference_answer:str|None=Field(default=None,alias="referenceAnswer",description="参考答案")
    scoring_points:list[str]|None=Field(default=None,alias="scoringPoints",description="评分要点")
    source:str|None=Field(default=None,description="题目来源")


class QuestionSaveRequest(BaseModel):
    ids:list[int]

#在prompt模板中接收llm输出面试题类
class QuestionItem(BaseModel):
    type:str
    difficulty:str
    question:str
    reference_answer:str=""
    scoring_points:list[str]=Field(default_factory=list)
    source:str

class QuestionLLMResult(BaseModel):
    questions:list[QuestionItem]

class QuestionItemResponse(BaseModel):
    id:int
    type:str
    difficulty:str
    question:str
    reference_answer:str=""
    scoring_points:list[str]=Field(default_factory=list)
    source:str
    is_saved:int

#生成面试题的返回格式
class QuestionCreateResponse(BaseModel):
    mode:QuestionMode
    position_id:int |None=Field(default=None)
    resume_id:int | None=Field(default=None)
    count:int
    questions:list[QuestionItemResponse]

class QuestionListInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)  #开启这个，是允许从orm对象中取值

    id:int
    position_id:Optional[int]
    resume_id:Optional[int]
    question_type:str
    difficulty:str
    question_content:str
    reference_answer:str=""
    scoring_points:list[str]=Field(default_factory=list)
    source:str
    is_saved:int

#获取题目列表响应类
class QuestionListResponse(BaseModel):
    total:int
    page: int
    page_size: int
    items:list[QuestionListInfo]
