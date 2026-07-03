from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.utils.exception import (
    general_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    sqlalchemy_error_handler,
)


def register_exception_handlers(app):
    """
    注册全局异常处理：子类在前，父类在后。具体的在前面，抽象在后
    :param app:
    :return:
    """
    #第一个参数是异常类类型，第二个是异常定义的方法
    app.add_exception_handler(HTTPException,http_exception_handler) #业务层面
    app.add_exception_handler(IntegrityError,integrity_error_handler) #数据完整性约束
    app.add_exception_handler(SQLAlchemyError,sqlalchemy_error_handler) #数据库层面的错误
    app.add_exception_handler(Exception,general_exception_handler) #兜底
