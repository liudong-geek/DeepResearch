"""
Content Scraper 基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ...shared import RateLimiter, CacheManager


class BaseContentScraper(ABC):
    """
    内容爬虫基类
    
    所有内容爬虫都应该继承此类
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
    async def get_content(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        获取内容列表
        
        Args:
            query: 搜索关键词或 URL
            limit: 返回内容数量
            
        Returns:
            内容列表
        """
        pass
    
    @abstractmethod
    async def extract_article(
        self,
        url: str
    ) -> Dict[str, Any]:
        """
        提取文章内容
        
        Args:
            url: 文章 URL
            
        Returns:
            文章内容
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

