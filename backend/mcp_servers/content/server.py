"""
Content MCP Server 实现
"""
from typing import Any, Dict, List
import json

from loguru import logger

from ..shared import BaseMCPServer, MCPTool, MCPResource, TextContent
from .scrapers import RedditContentScraper, ArticleContentScraper


class ContentMCPServer(BaseMCPServer):
    """
    Content MCP Server
    
    提供内容抓取功能（Reddit、文章等）
    """
    
    def __init__(self):
        super().__init__(
            name="content",
            version="1.0.0",
            rate_limit=0.3,  # 每 3.3 秒 1 个请求
            cache_ttl=7 * 24 * 3600,  # 7 天缓存
        )
        
        # 初始化爬虫
        self.scrapers = {
            "reddit": RedditContentScraper(self.rate_limiter, self.cache),
            "article": ArticleContentScraper(self.rate_limiter, self.cache),
        }
        
        logger.info(f"Content MCP Server 已初始化，支持: {list(self.scrapers.keys())}")
    
    def get_tools(self) -> List[MCPTool]:
        """获取工具列表"""
        return [
            MCPTool(
                name="get_content",
                description="获取内容列表（Reddit 帖子、文章等）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "内容来源（reddit/article）",
                            "enum": ["reddit", "article"],
                        },
                        "query": {
                            "type": "string",
                            "description": "搜索关键词或子版块名称（如 r/StandingDesk）",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回内容数量",
                            "default": 10,
                        },
                    },
                    "required": ["source", "query"],
                },
            ),
            MCPTool(
                name="extract_article",
                description="提取文章或帖子的详细内容",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "内容来源（reddit/article）",
                            "enum": ["reddit", "article"],
                        },
                        "url": {
                            "type": "string",
                            "description": "文章或帖子的 URL",
                        },
                    },
                    "required": ["source", "url"],
                },
            ),
        ]
    
    def get_resources(self) -> List[MCPResource]:
        """获取资源列表"""
        return [
            MCPResource(
                uri="content://sources",
                name="支持的内容来源列表",
                description="获取所有支持的内容来源",
                mime_type="application/json",
            ),
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """调用工具"""
        logger.info(f"调用工具: {tool_name}, 参数: {arguments}")
        
        result = None
        
        if tool_name == "get_content":
            result = await self._get_content(
                arguments["source"],
                arguments["query"],
                arguments.get("limit", 10)
            )
        
        elif tool_name == "extract_article":
            result = await self._extract_article(
                arguments["source"],
                arguments["url"]
            )
        
        else:
            raise ValueError(f"未知工具: {tool_name}")
        
        # 将结果转换为 TextContent 列表
        return [TextContent(text=json.dumps(result, ensure_ascii=False, indent=2))]
    
    async def _get_content(
        self,
        source: str,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """获取内容列表"""
        scraper = self.scrapers.get(source)
        if not scraper:
            raise ValueError(f"不支持的内容来源: {source}")
        
        return await scraper.get_content(query, limit)
    
    async def _extract_article(
        self,
        source: str,
        url: str
    ) -> Dict[str, Any]:
        """提取文章内容"""
        scraper = self.scrapers.get(source)
        if not scraper:
            raise ValueError(f"不支持的内容来源: {source}")
        
        return await scraper.extract_article(url)
    
    async def read_resource(self, uri: str) -> str:
        """读取资源"""
        if uri == "content://sources":
            return json.dumps({
                "sources": list(self.scrapers.keys()),
                "description": "支持的内容来源",
            }, ensure_ascii=False, indent=2)
        
        raise ValueError(f"未知资源: {uri}")

