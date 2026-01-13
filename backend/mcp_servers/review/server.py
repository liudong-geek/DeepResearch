"""
Review MCP Server 实现
"""
from typing import Any, Dict, List
import json

from loguru import logger

from ..shared import BaseMCPServer, MCPTool, MCPResource, TextContent
from .scrapers import AmazonReviewScraper, RedditReviewScraper


class ReviewMCPServer(BaseMCPServer):
    """
    Review MCP Server

    提供评论抓取和分析功能
    """

    def __init__(self):
        super().__init__(
            name="review",
            version="1.0.0",
            rate_limit=0.3,  # 每 3.3 秒 1 个请求（更保守）
            cache_ttl=7 * 24 * 3600,  # 7 天缓存
        )

        # 初始化爬虫
        self.scrapers = {
            "amazon": AmazonReviewScraper(self.rate_limiter, self.cache),
            "reddit": RedditReviewScraper(self.rate_limiter, self.cache),
        }

        logger.info(f"Review MCP Server 已初始化，支持: {list(self.scrapers.keys())}")
    
    def get_tools(self) -> List[MCPTool]:
        """获取工具列表"""
        return [
            MCPTool(
                name="get_reviews",
                description="获取产品评论列表",
                input_schema={
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "平台名称（amazon/reddit）",
                            "enum": ["amazon", "reddit"],
                        },
                        "product_id": {
                            "type": "string",
                            "description": "产品 ID 或 ASIN",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回评论数量",
                            "default": 50,
                        },
                    },
                    "required": ["platform", "product_id"],
                },
            ),
            MCPTool(
                name="analyze_reviews",
                description="分析评论，提取主题标签和情感",
                input_schema={
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "平台名称（amazon/reddit）",
                            "enum": ["amazon", "reddit"],
                        },
                        "product_id": {
                            "type": "string",
                            "description": "产品 ID 或 ASIN",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "分析评论数量",
                            "default": 100,
                        },
                    },
                    "required": ["platform", "product_id"],
                },
            ),
        ]
    
    def get_resources(self) -> List[MCPResource]:
        """获取资源列表"""
        return [
            MCPResource(
                uri="review://platforms",
                name="支持的平台列表",
                description="获取所有支持的评论平台",
                mime_type="application/json",
            ),
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """调用工具"""
        logger.info(f"调用工具: {tool_name}, 参数: {arguments}")
        
        result = None
        
        if tool_name == "get_reviews":
            result = await self._get_reviews(
                arguments["platform"],
                arguments["product_id"],
                arguments.get("limit", 50)
            )
        
        elif tool_name == "analyze_reviews":
            result = await self._analyze_reviews(
                arguments["platform"],
                arguments["product_id"],
                arguments.get("limit", 100)
            )
        
        else:
            raise ValueError(f"未知工具: {tool_name}")
        
        # 将结果转换为 TextContent 列表
        return [TextContent(text=json.dumps(result, ensure_ascii=False, indent=2))]
    
    async def _get_reviews(
        self,
        platform: str,
        product_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取评论列表"""
        scraper = self.scrapers.get(platform)
        if not scraper:
            raise ValueError(f"不支持的平台: {platform}")
        
        return await scraper.get_reviews(product_id, limit)
    
    async def _analyze_reviews(
        self,
        platform: str,
        product_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """分析评论"""
        scraper = self.scrapers.get(platform)
        if not scraper:
            raise ValueError(f"不支持的平台: {platform}")
        
        return await scraper.analyze_reviews(product_id, limit)

