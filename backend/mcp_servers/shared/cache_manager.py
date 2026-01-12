"""
缓存管理器

支持内存缓存和 Redis 缓存
"""
import hashlib
import json
import pickle
from datetime import timedelta
from typing import Any, Optional

from loguru import logger


class CacheManager:
    """
    缓存管理器（内存缓存）
    
    用法:
        cache = CacheManager(ttl=3600)
        cache.set("key", {"data": "value"})
        data = cache.get("key")
    """
    
    def __init__(self, ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            ttl: 缓存过期时间（秒）
        """
        self.ttl = ttl
        self._cache: dict[str, tuple[Any, float]] = {}
        logger.info(f"初始化缓存管理器: ttl={ttl}s")
    
    def _make_key(self, key: str) -> str:
        """生成缓存键（MD5 哈希）"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回 None
        """
        cache_key = self._make_key(key)
        
        if cache_key not in self._cache:
            return None
        
        value, expires_at = self._cache[cache_key]
        
        # 检查是否过期
        import time
        if time.time() > expires_at:
            del self._cache[cache_key]
            logger.debug(f"缓存已过期: {key[:50]}...")
            return None
        
        logger.debug(f"缓存命中: {key[:50]}...")
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），如果不指定则使用默认值
        """
        import time
        
        cache_key = self._make_key(key)
        expires_at = time.time() + (ttl or self.ttl)
        
        self._cache[cache_key] = (value, expires_at)
        logger.debug(f"缓存已设置: {key[:50]}... (ttl={ttl or self.ttl}s)")
    
    def delete(self, key: str) -> None:
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        cache_key = self._make_key(key)
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug(f"缓存已删除: {key[:50]}...")
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        logger.info("缓存已清空")
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)


class RedisCacheManager:
    """
    Redis 缓存管理器
    
    用法:
        cache = RedisCacheManager(redis_client, ttl=3600)
        await cache.set("key", {"data": "value"})
        data = await cache.get("key")
    """
    
    def __init__(self, redis_client: Any, ttl: int = 3600, prefix: str = "cache"):
        """
        初始化 Redis 缓存管理器
        
        Args:
            redis_client: Redis 客户端
            ttl: 缓存过期时间（秒）
            prefix: 缓存键前缀
        """
        self.redis = redis_client
        self.ttl = ttl
        self.prefix = prefix
        logger.info(f"初始化 Redis 缓存管理器: ttl={ttl}s, prefix={prefix}")
    
    def _make_key(self, key: str) -> str:
        """生成 Redis 键"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return f"{self.prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回 None
        """
        redis_key = self._make_key(key)
        
        try:
            data = await self.redis.get(redis_key)
            if data is None:
                return None
            
            # 反序列化
            value = pickle.loads(data)
            logger.debug(f"Redis 缓存命中: {key[:50]}...")
            return value
        except Exception as e:
            logger.error(f"Redis 获取缓存失败: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），如果不指定则使用默认值
        """
        redis_key = self._make_key(key)
        
        try:
            # 序列化
            data = pickle.dumps(value)
            
            # 设置缓存
            await self.redis.setex(
                redis_key,
                ttl or self.ttl,
                data
            )
            logger.debug(f"Redis 缓存已设置: {key[:50]}... (ttl={ttl or self.ttl}s)")
        except Exception as e:
            logger.error(f"Redis 设置缓存失败: {e}")

