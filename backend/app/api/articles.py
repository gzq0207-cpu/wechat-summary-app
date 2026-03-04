import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.core.config import get_db
from app.models.database import Article, Summary
from app.models.schemas import ArticleDetailResponse, ArticleResponse, SummaryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("", response_model=list[ArticleResponse])
def list_articles(
    account_id: int = Query(None, description="按公众号筛选"),
    date: str = Query(None, description="筛选日期 YYYY-MM-DD"),
    limit: int = Query(20, le=100),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """获取文章列表（支持分页和筛选）"""
    query = db.query(Article)
    
    if account_id:
        query = query.filter(Article.account_id == account_id)
    
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            next_date = target_date + timedelta(days=1)
            query = query.filter(
                Article.published_at >= target_date,
                Article.published_at < next_date
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    
    articles = query.order_by(desc(Article.published_at)).offset(skip).limit(limit).all()
    return articles


@router.get("/{article_id}", response_model=ArticleDetailResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """获取文章详情（包含摘要）"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return article


@router.get("/{article_id}/summary", response_model=SummaryResponse)
def get_article_summary(article_id: int, db: Session = Depends(get_db)):
    """获取文章摘要"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if not article.summary:
        raise HTTPException(status_code=404, detail="文章摘要未生成")
    
    return article.summary
