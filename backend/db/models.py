"""
数据库模型

使用 SQLAlchemy ORM
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ResearchTask(Base):
    """调研任务表"""
    
    __tablename__ = "research_tasks"
    
    # 主键
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # 基本信息
    keyword = Column(String(255), nullable=False, comment="产品关键词")
    market = Column(String(10), nullable=False, default="US", comment="目标市场")
    competitors = Column(JSON, nullable=False, comment="竞品列表")
    
    # 状态
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="任务状态: pending/running/completed/failed"
    )
    progress = Column(Integer, nullable=False, default=0, comment="进度 0-100")
    current_step = Column(String(255), comment="当前步骤")
    error_message = Column(Text, comment="错误信息")
    
    # 结果
    result = Column(JSON, comment="调研结果")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, comment="完成时间")
    
    # 索引
    __table_args__ = (
        Index("idx_research_tasks_status", "status"),
        Index("idx_research_tasks_created_at", "created_at"),
    )


class Evidence(Base):
    """证据表（存储原始数据源）"""
    
    __tablename__ = "evidence"
    
    # 主键
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # 关联任务
    task_id = Column(PGUUID(as_uuid=True), ForeignKey("research_tasks.id"), nullable=False)
    
    # 数据源信息
    source_type = Column(String(50), nullable=False, comment="数据源类型: product_page/review/spec")
    source_url = Column(Text, nullable=False, comment="数据源 URL")
    brand = Column(String(100), comment="品牌")
    
    # 原始数据
    raw_data = Column(JSON, nullable=False, comment="原始数据（JSON）")
    
    # 提取的关键信息
    extracted_info = Column(JSON, comment="提取的关键信息")
    
    # 元数据
    scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="抓取时间")
    content_hash = Column(String(64), comment="内容哈希（用于去重）")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    task = relationship("ResearchTask", backref="evidences")
    
    # 索引
    __table_args__ = (
        Index("idx_evidence_task_id", "task_id"),
        Index("idx_evidence_source_type", "source_type"),
        Index("idx_evidence_content_hash", "content_hash"),
    )


class Citation(Base):
    """引用表（结论→证据映射）"""
    
    __tablename__ = "citations"
    
    # 主键
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # 关联任务
    task_id = Column(PGUUID(as_uuid=True), ForeignKey("research_tasks.id"), nullable=False)
    
    # 关联证据
    evidence_id = Column(PGUUID(as_uuid=True), ForeignKey("evidence.id"), nullable=False)
    
    # 结论信息
    conclusion_type = Column(String(50), nullable=False, comment="结论类型: price/spec/review_insight")
    conclusion_text = Column(Text, nullable=False, comment="结论文本")
    
    # 引用位置
    section = Column(String(100), comment="报告章节")
    
    # 置信度
    confidence = Column(Float, comment="置信度 0-1")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    task = relationship("ResearchTask", backref="citations")
    evidence = relationship("Evidence", backref="citations")
    
    # 索引
    __table_args__ = (
        Index("idx_citations_task_id", "task_id"),
        Index("idx_citations_evidence_id", "evidence_id"),
        Index("idx_citations_conclusion_type", "conclusion_type"),
    )


class ScraperCache(Base):
    """爬虫缓存表"""
    
    __tablename__ = "scraper_cache"
    
    # 主键
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # 缓存键
    cache_key = Column(String(255), nullable=False, unique=True, comment="缓存键（URL hash）")
    
    # 缓存数据
    data = Column(JSON, nullable=False, comment="缓存数据")
    
    # 元数据
    url = Column(Text, comment="原始 URL")
    scraper_type = Column(String(50), comment="爬虫类型")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, comment="过期时间")
    
    # 索引
    __table_args__ = (
        Index("idx_scraper_cache_expires_at", "expires_at"),
    )

