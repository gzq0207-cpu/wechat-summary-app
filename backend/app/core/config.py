from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """应用配置管理"""
    # 数据库
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/wechat_summary")
    
    # 应用
    app_name: str = "WeChat Summary"
    app_version: str = "1.0.0"
    fastapi_env: str = os.getenv("FASTAPI_ENV", "development")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]
    api_v1_str: str = "/api/v1"
    
    # LLM配置
    llm_provider: str = os.getenv("LLM_PROVIDER", "baidu")
    baidu_api_key: str = os.getenv("BAIDU_API_KEY", "")
    baidu_secret_key: str = os.getenv("BAIDU_SECRET_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # 爬虫配置
    wechat_login_username: str = os.getenv("WECHAT_LOGIN_USERNAME", "")
    wechat_login_password: str = os.getenv("WECHAT_LOGIN_PASSWORD", "")
    crawl_delay_seconds: int = int(os.getenv("CRAWL_DELAY_SECONDS", "2"))
    headless_browser: bool = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"
    browser_timeout_seconds: int = int(os.getenv("BROWSER_TIMEOUT_SECONDS", "30"))
    
    # 定时任务
    schedule_timezone: str = os.getenv("SCHEDULE_TIMEZONE", "Asia/Shanghai")
    crawl_schedule_hour: int = int(os.getenv("CRAWL_SCHEDULE_HOUR", "9"))
    crawl_schedule_minute: int = int(os.getenv("CRAWL_SCHEDULE_MINUTE", "0"))

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
