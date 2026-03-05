from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import json

class Settings(BaseSettings):
    """应用配置管理"""
    # 数据库
    database_url: str = "postgresql://user:password@localhost:5432/wechat_summary"

    # 应用
    app_name: str = "WeChat Summary"
    app_version: str = "1.0.0"
    fastapi_env: str = "development"
    secret_key: str = "your-secret-key-change-in-production"
    api_v1_str: str = "/api/v1"

    # CORS - 支持通过环境变量 CORS_ORIGINS 配置（逗号分隔或 JSON 数组）
    # Railway 示例：CORS_ORIGINS=https://yourapp.railway.app
    # 本地默认包含 localhost 各端口
    cors_origins: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # LLM配置
    llm_provider: str = "baidu"
    baidu_api_key: str = ""
    baidu_secret_key: str = ""
    openai_api_key: str = ""

    # 爬虫配置
    wechat_login_username: str = ""
    wechat_login_password: str = ""
    crawl_delay_seconds: int = 2
    headless_browser: bool = True
    browser_timeout_seconds: int = 30

    # 定时任务
    schedule_timezone: str = "Asia/Shanghai"
    crawl_schedule_hour: int = 9
    crawl_schedule_minute: int = 0

    class Config:
        case_sensitive = False
        env_file = ".env"

settings = Settings()

# SQLAlchemy数据库连接
engine = create_engine(
    settings.database_url,
    poolclass=NullPool if "sqlite" in settings.database_url else None,
    echo=settings.fastapi_env == "development"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM基类
Base = declarative_base()

def get_db():
    """数据库会话依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
