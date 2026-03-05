import logging
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings, engine, Base
from app.api import accounts, articles, tasks
from app.tasks.scheduler import start_scheduler, shutdown_scheduler

# 配置日志 - 仅 stdout（Railway 会捕获 stdout/stderr 到日志查看器）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

# 创建数据库表 - 可容错
def init_db():
    """初始化数据库表，失败时记录错误但不中断启动"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表已创建")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        logger.error("请确保 DATABASE_URL 环境变量已设置且数据库可访问")

init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"应用启动: {settings.app_name} v{settings.app_version}")
    logger.info(f"环境: {settings.fastapi_env}")
    start_scheduler()

    yield

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

# 注册API路由（必须在 StaticFiles 挂载之前注册）
app.include_router(accounts.router, prefix=settings.api_v1_str)
app.include_router(articles.router, prefix=settings.api_v1_str)
app.include_router(tasks.router, prefix=settings.api_v1_str)

@app.get("/health")
async def health_check():
    """健康检查（用于云部署）"""
    return {"status": "healthy"}

# 挂载 React SPA 静态文件
# html=True 启用 SPA fallback：未匹配的路径返回 index.html（替代 nginx 的 try_files）
# 守卫确保本地 docker-compose 开发时（无 /app/static）不会崩溃
_static_dir = "/app/static"
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
    logger.info(f"React SPA 已挂载：{_static_dir}")
else:
    logger.warning(f"静态目录 {_static_dir} 不存在，React SPA 未挂载（本地开发模式？）")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.fastapi_env == "development"
    )
