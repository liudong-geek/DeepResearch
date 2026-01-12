"""
限速器模块

实现 Token Bucket 算法，防止爬虫被封
"""
import asyncio
import time
from typing import Dict, Optional

from loguru import logger


class RateLimiter:
    """
    限速器（Token Bucket 算法）
    
    用法:
        limiter = RateLimiter(rate=1.0, burst=2)
        await limiter.acquire()  # 等待直到可以执行
    """
    
    def __init__(self, rate: float, burst: int = 1):
        """
        初始化限速器
        
        Args:
            rate: 每秒允许的请求数（例如 0.5 表示每 2 秒 1 个请求）
            burst: 突发容量（允许的最大令牌数）
        """
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
        
        logger.info(f"初始化限速器: rate={rate}/s, burst={burst}")
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        获取令牌（如果不足则等待）
        
        Args:
            tokens: 需要的令牌数
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                
                # 补充令牌
                self.tokens = min(
                    self.burst,
                    self.tokens + elapsed * self.rate
                )
                self.last_update = now
                
                # 如果令牌足够，消耗并返回
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # 计算需要等待的时间
                wait_time = (tokens - self.tokens) / self.rate
                logger.debug(f"限速中，等待 {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
    
    def try_acquire(self, tokens: int = 1) -> bool:
        """
        尝试获取令牌（非阻塞）
        
        Args:
            tokens: 需要的令牌数
            
        Returns:
            是否成功获取
        """
        now = time.monotonic()
        elapsed = now - self.last_update
        
        # 补充令牌
        self.tokens = min(
            self.burst,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now
        
        # 如果令牌足够，消耗并返回 True
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False


class MultiRateLimiter:
    """
    多域名限速器
    
    为不同的域名维护独立的限速器
    """
    
    def __init__(self, default_rate: float = 1.0, default_burst: int = 1):
        """
        初始化多域名限速器
        
        Args:
            default_rate: 默认速率
            default_burst: 默认突发容量
        """
        self.default_rate = default_rate
        self.default_burst = default_burst
        self.limiters: Dict[str, RateLimiter] = {}
        self._lock = asyncio.Lock()
    
    async def acquire(self, domain: str, tokens: int = 1) -> None:
        """
        为指定域名获取令牌
        
        Args:
            domain: 域名
            tokens: 需要的令牌数
        """
        async with self._lock:
            if domain not in self.limiters:
                self.limiters[domain] = RateLimiter(
                    rate=self.default_rate,
                    burst=self.default_burst
                )
        
        await self.limiters[domain].acquire(tokens)
    
    def set_rate(self, domain: str, rate: float, burst: Optional[int] = None) -> None:
        """
        为指定域名设置速率
        
        Args:
            domain: 域名
            rate: 速率
            burst: 突发容量（可选）
        """
        self.limiters[domain] = RateLimiter(
            rate=rate,
            burst=burst or self.default_burst
        )
        logger.info(f"设置 {domain} 限速: {rate}/s")

