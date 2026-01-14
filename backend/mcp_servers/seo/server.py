"""
SEO MCP Server 实现
提供 Google 搜索和 SEO 分析功能
"""
from typing import Any, Dict, List
import json

from loguru import logger

from ..shared import BaseMCPServer, MCPTool, MCPResource, TextContent
from .scrapers import GoogleSearchScraper


class SEOMCPServer(BaseMCPServer):
    """
    SEO MCP Server

    提供 Google 搜索和 SEO 分析功能
    使用 Google Custom Search API（免费配额：100 次/天）
    """

    def __init__(self):
        super().__init__(
            name="seo",
            version="1.0.0",
            rate_limit=1.0,  # 每秒 1 个请求（保护 API 配额）
            cache_ttl=7 * 24 * 3600,  # 7 天缓存
        )

        # 初始化爬虫
        self.google_scraper = GoogleSearchScraper(self.rate_limiter, self.cache)

        logger.info("SEO MCP Server 已初始化")

    def get_resources(self) -> List[MCPResource]:
        """返回可用的资源列表"""
        return []  # SEO MCP 不提供资源

    def get_tools(self) -> List[MCPTool]:
        """返回可用的工具列表"""
        return [
            MCPTool(
                name="google_search",
                description="执行 Google 搜索，返回搜索结果",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "market": {
                            "type": "string",
                            "description": "市场代码（如 us, uk）",
                            "default": "us"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "返回结果数量（最多 10）",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="get_serp_features",
                description="获取 SERP 特性（搜索结果页特征）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "market": {
                            "type": "string",
                            "description": "市场代码",
                            "default": "us"
                        }
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="analyze_competitor_rankings",
                description="分析竞品在搜索结果中的排名",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "competitors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "竞品品牌列表"
                        },
                        "market": {
                            "type": "string",
                            "description": "市场代码",
                            "default": "us"
                        }
                    },
                    "required": ["keyword", "competitors"]
                }
            ),
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """调用工具"""
        try:
            if name == "google_search":
                query = arguments["query"]
                market = arguments.get("market", "us")
                num_results = arguments.get("num_results", 10)

                results = await self.google_scraper.search(query, market, num_results)

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(results, ensure_ascii=False, indent=2)
                    )
                ]

            elif name == "get_serp_features":
                query = arguments["query"]
                market = arguments.get("market", "us")

                features = await self.google_scraper.get_serp_features(query, market)

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(features, ensure_ascii=False, indent=2)
                    )
                ]

            elif name == "analyze_competitor_rankings":
                keyword = arguments["keyword"]
                competitors = arguments["competitors"]
                market = arguments.get("market", "us")

                rankings = await self.google_scraper.analyze_competitor_rankings(
                    keyword, competitors, market
                )

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(rankings, ensure_ascii=False, indent=2)
                    )
                ]

            else:
                raise ValueError(f"未知工具: {name}")

        except Exception as e:
            logger.error(f"❌ 工具调用失败 ({name}): {e}")
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, ensure_ascii=False)
                )
            ]

