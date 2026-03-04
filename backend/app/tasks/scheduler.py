import logging
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings, SessionLocal
from app.models.database import PublicAccount, CrawlLog
from app.crawlers.wechat import WechatCrawler
from app.summarizer.service import SummaryService

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True, timezone=settings.schedule_timezone)

async def crawl_and_summarize_job():
    """爬虫和摘要生成任务"""
    db = SessionLocal()
    try:
        logger.info("="*50)
        logger.info("开始执行爬虫和摘要任务")
        logger.info("="*50)
        
        # 获取所有启用的公众号
        accounts = db.query(PublicAccount).filter(PublicAccount.is_active == True).all()
        
        if not accounts:
            logger.warning("没有启用的公众号")
            return
        
        crawler = WechatCrawler(headless=settings.headless_browser, timeout=settings.browser_timeout_seconds)
        summarizer = SummaryService()
        
        await crawler.initialize()
        
        for account in accounts:
            start_time = datetime.now()
            status = "success"
            article_count = 0
            error_message = None
            
            try:
                logger.info(f"开始爬取公众号: {account.name}")
                
                # 这是简化实现，实际需要完整的爬虫逻辑和登录认证
                # articles = await crawler.get_articles_list(account.account_id)
                articles = []  # 临时返回空列表
                
                article_count = len(articles)
                
                if articles:
                    logger.info(f"爬取到 {article_count} 篇新文章")
                    
                    # 生成摘要
                    summary_count = await summarizer.batch_generate_summaries(
                        account.id, db, limit=article_count
                    )
                    logger.info(f"成功生成 {summary_count} 篇摘要")
                else:
                    logger.info(f"公众号 {account.name} 没有新文章")
                
                # 更新最后爬取时间
                account.last_crawled_at = datetime.now()
            
            except Exception as e:
                status = "failed"
                error_message = str(e)
                logger.error(f"爬取公众号 {account.name} 失败: {error_message}")
            
            finally:
                # 记录爬虫日志
                duration = int((datetime.now() - start_time).total_seconds())
                log = CrawlLog(
                    account_id=account.id,
                    status=status,
                    article_count=article_count,
                    error_message=error_message,
                    duration_seconds=duration
                )
                db.add(log)
                db.commit()
        
        await crawler.close()
        
        logger.info("="*50)
        logger.info("爬虫和摘要任务完成")
        logger.info("="*50)
    
    except Exception as e:
        logger.error(f"爬虫任务异常: {str(e)}")
    
    finally:
        db.close()


def schedule_crawl_job():
    """添加爬虫定时任务"""
    # 使用Cron表达式定时
    trigger = CronTrigger(
        hour=settings.crawl_schedule_hour,
        minute=settings.crawl_schedule_minute,
        timezone=settings.schedule_timezone
    )
    
    scheduler.add_job(
        func=lambda: asyncio.run(crawl_and_summarize_job()),
        trigger=trigger,
        id="crawl_and_summarize",
        name="爬虫和摘要任务",
        replace_existing=True
    )
    
    logger.info(f"已添加定时任务: 每天 {settings.crawl_schedule_hour}:{settings.crawl_schedule_minute:02d} 执行爬虫任务")


def start_scheduler():
    """启动调度器"""
    if not scheduler.running:
        schedule_crawl_job()
        scheduler.start()
        logger.info("APScheduler已启动")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler已关闭")
