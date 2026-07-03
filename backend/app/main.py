
import sys
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
BACKEND_DIR = APP_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from api import compare, dashboard, evaluations, hr, intake, position, question, recordings, resume, screening, summary
from database import Base, engine
from models import JobPosition  # noqa: F401
from models.intake import RecruitmentDocRow, RecruitmentMessage, RecruitmentSyncEvent  # noqa: F401
from utils.exception_handlers import register_exception_handlers


app = FastAPI(
    title="AI 招聘提效助手 API",
    description="面向企业微信招聘消息采集、腾讯文档同步和招聘看板的 AI Demo 接口",
    version="1.0.0",
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成")


@app.get("/")
def root():
    return {"message": "AI 招聘提效助手 API 运行中", "docs": "/docs"}


app.include_router(position.router)
app.include_router(hr.router)
app.include_router(resume.router)
app.include_router(screening.router)
app.include_router(question.router)
app.include_router(recordings.router)
app.include_router(summary.router)
app.include_router(evaluations.router)
app.include_router(compare.router)
app.include_router(dashboard.router)
app.include_router(intake.router)

