from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

def success_response(message:str="success",data=None):
    content ={
        "code":200,
        "message":message,
        "data":data  #拿刚刚的用户举例，data定义在pydantic中，在schemas users中
    }

    #目标：把任何FastAPI、Pydantic、ORM对象 都要正常响应 -> code、message、data
    return JSONResponse(content=jsonable_encoder(content))