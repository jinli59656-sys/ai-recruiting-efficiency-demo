from pydantic import BaseModel


#hr登录的用户和密码
class HRRequest(BaseModel):
    hr_name:str
    password:str

class UserRequest(BaseModel):
    username:str
    password:str