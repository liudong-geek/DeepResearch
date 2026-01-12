"""
MCP Server 基类

所有 MCP Server 的基类，提供通用功能
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json

from loguru import logger
from pydantic import BaseModel

from .cache_manager import CacheManager
from .rate_limiter import RateLimiter


class MCPTool(BaseModel):
    """MCP 工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPResource(BaseModel):
    """MCP 资源定义"""
    uri: str
    name: str
    description: str
    mime_type: str


class TextContent(BaseModel):
    """文本内容"""
    type: str = "text"
    text: str


class BaseMCPServer(ABC):
    """
    MCP Server 基类
    
    所有 MCP Server 都应该继承此类
    """
    
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        rate_limit: float = 1.0,
        cache_ttl: int = 3600,
    ):
        """
        初始化 MCP Server
        
        Args:
            name: Server 名称
            version: Server 版本
            rate_limit: 限速（请求/秒）
            cache_ttl: 缓存过期时间（秒）
        """
        self.name = name
        self.version = version
        
        # 初始化限速器
        self.rate_limiter = RateLimiter(rate=rate_limit, burst=2)
        
        # 初始化缓存
        self.cache = CacheManager(ttl=cache_ttl)
        
        logger.info(
            f"初始化 MCP Server: {name} v{version} "
            f"(rate={rate_limit}/s, cache_ttl={cache_ttl}s)"
        )
    
    @abstractmethod
    def get_tools(self) -> List[MCPTool]:
        """
        获取 Server 提供的工具列表
        
        Returns:
            工具列表
        """
        pass
    
    @abstractmethod
    def get_resources(self) -> List[MCPResource]:
        """
        获取 Server 提供的资源列表
        
        Returns:
            资源列表
        """
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        pass
    
    async def _fetch_with_cache(
        self,
        cache_key: str,
        fetch_func: callable,
        ttl: Optional[int] = None,
    ) -> Any:
        """
        带缓存的数据获取
        
        Args:
            cache_key: 缓存键
            fetch_func: 数据获取函数（异步）
            ttl: 缓存过期时间（可选）
            
        Returns:
            数据
        """
        # 尝试从缓存获取
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # 限速
        await self.rate_limiter.acquire()
        
        # 获取数据
        logger.info(f"缓存未命中，正在获取数据: {cache_key[:50]}...")
        data = await fetch_func()
        
        # 存入缓存
        self.cache.set(cache_key, data, ttl=ttl)
        
        return data
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取 Server 信息
        
        Returns:
            Server 信息
        """
        return {
            "name": self.name,
            "version": self.version,
            "tools": [tool.model_dump() for tool in self.get_tools()],
            "resources": [resource.model_dump() for resource in self.get_resources()],
            "cache_size": self.cache.size(),
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态
        """
        return {
            "status": "healthy",
            "name": self.name,
            "version": self.version,
            "cache_size": self.cache.size(),
        }

