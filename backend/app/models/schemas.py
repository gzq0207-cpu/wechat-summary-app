from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class PublicAccountCreate(BaseModel):
    """创建公众号请求模型"""
    name: str
    account_id: str
    subscribe_url: Optional[str] = None
    description: Optional[str] = None


class PublicAccountUpdate(BaseModel):
    """更新公众号请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PublicAccountResponse(BaseModel):
    """公众号响应模型"""
    id: int
    name: str
    account_id: str
    subscribe_url: Optional[str]
    description: Optional[str]
    is_active: bool
    last_crawled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    account_id: int
    title: str
    url: str
    author: Optional[str]
    published_at: datetime
    read_count: int
    like_count: int
    cover_image_url: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SummaryResponse(BaseModel):
    """摘要响应模型"""
    id: int
    article_id: int
    summary_text: str
    summary_length: Optional[int]
    llm_provider: Optional[str]
    generation_time_ms: Optional[int]
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ArticleDetailResponse(ArticleResponse):
    """文章详情响应模型（包含摘要）"""
    summary: Optional[SummaryResponse]
    

class CrawlLogResponse(BaseModel):
    """爬虫日志响应模型"""
    id: int
    account_id: int
    status: str
    article_count: int
    new_article_count: int
    error_message: Optional[str]
    duration_seconds: Optional[int]
    run_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    is_running: bool
    last_crawl_time: Optional[datetime]
    next_crawl_time: Optional[datetime]
    total_accounts: int
    active_accounts: int
