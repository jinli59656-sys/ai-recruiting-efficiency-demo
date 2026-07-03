from passlib.context import CryptContext

#验证密码的
#用一下加密算法进行加密
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

#密码加密
def get_hash_password(password:str):
    return pwd_context.hash(password)

#密码验证
def verify_password(plan_password,hashed_password):
    return pwd_context.verify(plan_password,hashed_password)