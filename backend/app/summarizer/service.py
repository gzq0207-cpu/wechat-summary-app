import logging
from sqlalchemy.orm import Session
from app.models.database import Article, Summary
from app.summarizer.client import create_summarizer
from app.core.config import settings

logger = logging.getLogger(__name__)

class SummaryService:
    """摘要服务"""
    
    def __init__(self):
        self.client = create_summarizer(
            provider=settings.llm_provider,
            api_key=settings.baidu_api_key,
            secret_key=settings.baidu_secret_key
        )
    
    async def generate_summary(self, article_id: int, db: Session) -> bool:
        """
        为文章生成摘要
        
        Args:
            article_id: 文章ID
            db: 数据库会话
        
        Returns:
            是否生成成功
        """
        try:
            article = db.query(Article).filter(Article.id == article_id).first()
            if not article:
                logger.error(f"文章 {article_id} 不存在")
                return False
            
            # 检查是否已有摘要
            existing_summary = db.query(Summary).filter(Summary.article_id == article_id).first()
            if existing_summary:
                logger.info(f"文章 {article_id} 已有摘要，跳过生成")
                return True
            
            # 如果没有纯文本，使用content
            text_to_summarize = article.plain_text or article.content or ""
            if not text_to_summarize:
                logger.warning(f"文章 {article_id} 没有内容可摘要")
                return False
            
            # 调用LLM API生成摘要
            result = await self.client.summarize(text_to_summarize, max_length=500)
            if not result:
                logger.error(f"生成摘要失败: {article_id}")
                return False
            
            # 保存摘要
            summary = Summary(
                article_id=article_id,
                summary_text=result["summary_text"],
                summary_length=len(result["summary_text"]),
                llm_provider=result.get("provider"),
                generation_time_ms=result.get("generation_time_ms"),
                cost=str(result.get("cost"))
            )
            db.add(summary)
            db.commit()
            
            logger.info(f"成功生成文章 {article_id} 的摘要")
            return True
        
        except Exception as e:
            logger.error(f"生成摘要异常 {article_id}: {str(e)}")
            db.rollback()
            return False
    
    async def batch_generate_summaries(self, account_id: int, db: Session, limit: int = 100) -> int:
        """
        批量为公众号的文章生成摘要
        
        Args:
            account_id: 公众号ID
            db: 数据库会话
            limit: 最多处理数量
        
        Returns:
            成功生成的摘要数
        """
        # 查找没有摘要的文章
        articles = db.query(Article).filter(
            Article.account_id == account_id,
            ~Article.summary.any()
        ).limit(limit).all()
        
        success_count = 0
        for article in articles:
            if await self.generate_summary(article.id, db):
                success_count += 1
        
        logger.info(f"为公众号 {account_id} 成功生成 {success_count}/{len(articles)} 篇摘要")
        return success_count
