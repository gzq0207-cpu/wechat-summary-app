import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.core.config import get_db
from app.models.database import PublicAccount, Article, Summary, CrawlLog
from app.models.schemas import (
    PublicAccountCreate, PublicAccountUpdate, PublicAccountResponse,
    ArticleDetailResponse, ArticleResponse, SummaryResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("", response_model=list[PublicAccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    """获取所有追踪的公众号"""
    accounts = db.query(PublicAccount).order_by(desc(PublicAccount.created_at)).all()
    return accounts


@router.get("/{account_id}", response_model=PublicAccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """获取公众号详情"""
    account = db.query(PublicAccount).filter(PublicAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="公众号不存在")
    return account


@router.post("", response_model=PublicAccountResponse)
def create_account(account: PublicAccountCreate, db: Session = Depends(get_db)):
    """添加新的公众号追踪"""
    # 检查是否已存在
    existing = db.query(PublicAccount).filter(
        PublicAccount.account_id == account.account_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="公众号已存在")
    
    new_account = PublicAccount(
        name=account.name,
        account_id=account.account_id,
        subscribe_url=account.subscribe_url,
        description=account.description
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    logger.info(f"新增公众号: {account.name} ({account.account_id})")
    return new_account


@router.put("/{account_id}", response_model=PublicAccountResponse)
def update_account(account_id: int, account: PublicAccountUpdate, db: Session = Depends(get_db)):
    """更新公众号信息"""
    db_account = db.query(PublicAccount).filter(PublicAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="公众号不存在")
    
    if account.name:
        db_account.name = account.name
    if account.description is not None:
        db_account.description = account.description
    if account.is_active is not None:
        db_account.is_active = account.is_active
    
    db.commit()
    db.refresh(db_account)
    
    logger.info(f"更新公众号: {db_account.name}")
    return db_account


@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """删除公众号追踪"""
    account = db.query(PublicAccount).filter(PublicAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="公众号不存在")
    
    db.delete(account)
    db.commit()
    
    logger.info(f"删除公众号: {account.name}")
    return {"message": "公众号已删除"}
