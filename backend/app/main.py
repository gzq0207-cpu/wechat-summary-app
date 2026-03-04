import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings, engine, Base
from app.api import accounts, articles, tasks
from app.tasks.scheduler import start_scheduler, shutdown_scheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)
logger.info("数据库表已创建")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动事件
    logger.info(f"应用启动: {settings.app_name} v{settings.app_version}")
    logger.info(f"环境: {settings.fastapi_env}")
    start_scheduler()
    
    yield
    
    # 关闭事件
    logger.info("应用关闭中...")
    shutdown_scheduler()
    logger.info("应用已关闭")

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="微信公众号文章聚合摘要系统",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(accounts.router, prefix=settings.api_v1_str)
app.include_router(articles.router, prefix=settings.api_v1_str)
app.include_router(tasks.router, prefix=settings.api_v1_str)

@app.get("/")
async def root():
    """根路由"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查（用于云部署）"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.fastapi_env == "development"
    )
