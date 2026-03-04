import logging
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.config import get_db
from app.models.schemas import TaskStatusResponse, CrawlLogResponse
from app.models.database import PublicAccount, CrawlLog
from app.tasks.scheduler import scheduler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/run-now")
async def run_crawl_task_now(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """手动触发爬虫任务（立即执行）"""
    # 在后台运行爬虫任务
    background_tasks.add_task(run_crawl_and_summarize, db)
    
    return {
        "message": "爬虫任务已提交",
        "status": "queued",
        "triggered_at": datetime.now().isoformat()
    }


@router.get("/status", response_model=TaskStatusResponse)
def get_task_status(db: Session = Depends(get_db)):
    """查看任务执行状态"""
    jobs = scheduler.get_jobs()
    crawl_job = next((job for job in jobs if job.name == "crawl_and_summarize"), None)
    
    active_accounts = db.query(PublicAccount).filter(PublicAccount.is_active == True).count()
    total_accounts = db.query(PublicAccount).count()
    
    return TaskStatusResponse(
        is_running=bool(crawl_job),
        last_crawl_time=crawl_job.next_run_time if crawl_job else None,
        next_crawl_time=crawl_job.next_run_time if crawl_job else None,
        total_accounts=total_accounts,
        active_accounts=active_accounts
    )


@router.get("/logs", response_model=list[CrawlLogResponse])
def get_crawl_logs(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取爬虫任务日志"""
    logs = db.query(CrawlLog).order_by(CrawlLog.run_at.desc()).limit(limit).all()
    return logs


async def run_crawl_and_summarize(db: Session):
    """执行爬虫和摘要任务（不在路由中实现，避免阻塞）"""
    # 这个函数会被APScheduler或BackgroundTasks调用
    # 具体实现在 tasks/jobs.py
    pass
