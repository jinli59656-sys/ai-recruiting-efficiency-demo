from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "hr_assistant"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "resume-files"
    MINIO_BUCKET1: str = "recording-files"
    MINIO_REGION: str = ""
    MINIO_PUBLIC_BASE_URL: str = ""

    MILVUS_HOST:str="localhost"
    MILVUS_PORT:int=19530
    MILVUS_COLLECTION_NAME:str="resume_embeddings"

    QWEN_EMBEDDING_MODEL:str="text-embedding-v4"
    QWEN_EMBEDDING_DIMENSIONS:int=1536

    FUN_ASR_MODEL:str="fun-asr-realtime"

    QWEN_API_KEY:str=""
    QWEN_BASE_URL:str="https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL:str="qwen-plus"
    QWEN_VISION_MODEL:str="qwen-vl-plus"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
