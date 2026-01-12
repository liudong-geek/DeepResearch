"""
Review Scraper 基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ...shared import RateLimiter, CacheManager


class BaseReviewScraper(ABC):
    """
    评论爬虫基类
    
    所有评论爬虫都应该继承此类
    """
    
    def __init__(self, rate_limiter: RateLimiter, cache: CacheManager):
        """
        初始化爬虫
        
        Args:
            rate_limiter: 限速器
            cache: 缓存管理器
        """
        self.rate_limiter = rate_limiter
        self.cache = cache
    
    @abstractmethod
    async def get_reviews(
        self,
        product_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取评论列表
        
        Args:
            product_id: 产品 ID
            limit: 返回评论数量
            
        Returns:
            评论列表
        """
        pass
    
    @abstractmethod
    async def analyze_reviews(
        self,
        product_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        分析评论
        
        Args:
            product_id: 产品 ID
            limit: 分析评论数量
            
        Returns:
            分析结果
        """
        pass
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余空白
        text = " ".join(text.split())
        
        return text.strip()

