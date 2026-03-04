from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.config import Base

class PublicAccount(Base):
    """微信公众号模型"""
    __tablename__ = "public_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)  # 公众号名称
    account_id = Column(String(255), unique=True, nullable=False)  # 微信账号ID
    subscribe_url = Column(String(500), nullable=True)  # 订阅链接
    description = Column(Text, nullable=True)  # 公众号描述
    is_active = Column(Boolean, default=True)  # 是否启用追踪
    last_crawled_at = Column(DateTime, nullable=True)  # 最后爬取时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    articles = relationship("Article", back_populates="account", cascade="all, delete-orphan")
    crawl_logs = relationship("CrawlLog", back_populates="account", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_account_id', account_id),
        Index('idx_is_active', is_active),
    )


class Article(Base):
    """文章模型"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("public_accounts.id"), nullable=False, index=True)
    title = Column(String(500), index=True, nullable=False)  # 文章标题
    content = Column(Text, nullable=True)  # 文章内容（HTML）
    plain_text = Column(Text, nullable=True)  # 纯文本内容
    url = Column(String(1000), unique=True, nullable=False)  # 文章链接
    author = Column(String(255), nullable=True)  # 作者
    published_at = Column(DateTime, index=True, nullable=False)  # 发布时间
    read_count = Column(Integer, default=0)  # 阅读数
    like_count = Column(Integer, default=0)  # 点赞数
    cover_image_url = Column(String(500), nullable=True)  # 封面图
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    account = relationship("PublicAccount", back_populates="articles")
    summary = relationship("Summary", uselist=False, back_populates="article", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_account_id_published', 'account_id', 'published_at', postgresql_using='btree'),
        Index('idx_created_at', 'created_at'),
    )


class Summary(Base):
    """摘要模型"""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, unique=True, index=True)
    summary_text = Column(Text, nullable=False)  # 摘要内容
    summary_length = Column(Integer, nullable=True)  # 摘要长度（字数）
    llm_provider = Column(String(50), nullable=True)  # 使用的LLM供应商
    generation_time_ms = Column(Integer, nullable=True)  # 生成耗时（毫秒）
    cost = Column(String(50), nullable=True)  # API调用成本
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    article = relationship("Article", back_populates="summary")
    
    __table_args__ = (
        Index('idx_generated_at', 'generated_at'),
    )


class CrawlLog(Base):
    """爬虫任务日志模型"""
    __tablename__ = "crawl_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("public_accounts.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # success, failed, partial
    article_count = Column(Integer, default=0)  # 本次爬取的文章数
    new_article_count = Column(Integer, default=0)  # 新增文章数
    error_message = Column(Text, nullable=True)  # 错误信息
    duration_seconds = Column(Integer, nullable=True)  # 爬取耗时（秒）
    run_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    account = relationship("PublicAccount", back_populates="crawl_logs")
    
    __table_args__ = (
        Index('idx_account_id_run_at', 'account_id', 'run_at', postgresql_using='btree'),
    )
