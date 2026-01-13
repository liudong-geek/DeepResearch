"""
E-commerce MCP Server 实现
"""
from typing import Any, Dict, List
import json

from loguru import logger

from ..shared import BaseMCPServer, MCPTool, MCPResource, TextContent
from .scrapers import UpliftScraper, JarvisScraper, VariScraper, GenericScraper, MonopriceScraper


class EcommerceMCPServer(BaseMCPServer):
    """
    E-commerce MCP Server

    提供电商产品信息抓取功能
    """

    def __init__(self):
        super().__init__(
            name="ecommerce",
            version="1.0.0",
            rate_limit=0.5,  # 每 2 秒 1 个请求
            cache_ttl=7 * 24 * 3600,  # 7 天缓存
        )

        # 初始化爬虫
        # Premium 品牌（专用爬虫）
        self.scrapers = {
            "uplift": UpliftScraper(self.rate_limiter, self.cache),
            "jarvis": JarvisScraper(self.rate_limiter, self.cache),
            "vari": VariScraper(self.rate_limiter, self.cache),
            "humanscale": GenericScraper("Humanscale", self.rate_limiter, self.cache),
        }

        # Mid-range 品牌（通用爬虫）
        self.scrapers.update({
            "flexispot": GenericScraper("FlexiSpot", self.rate_limiter, self.cache),
            "autonomous": GenericScraper("Autonomous", self.rate_limiter, self.cache),
        })

        # Budget 品牌（通用爬虫 + 专用爬虫）
        self.scrapers.update({
            "ikea": GenericScraper("IKEA", self.rate_limiter, self.cache),
            "monoprice": MonopriceScraper(self.rate_limiter, self.cache),  # 专用爬虫（处理 Cloudflare）
        })

        logger.info(f"E-commerce MCP Server 已初始化，支持: {list(self.scrapers.keys())}")
    
    def get_tools(self) -> List[MCPTool]:
        """获取工具列表"""
        # 动态生成支持的品牌列表
        supported_brands = list(self.scrapers.keys())

        return [
            MCPTool(
                name="get_product_info",
                description="获取产品基本信息（价格、标题、描述等）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "brand": {
                            "type": "string",
                            "description": f"品牌名称（{'/'.join(supported_brands)}）",
                            "enum": supported_brands,
                        },
                        "url": {
                            "type": "string",
                            "description": "产品页面 URL",
                        },
                    },
                    "required": ["brand", "url"],
                },
            ),
            MCPTool(
                name="get_product_specs",
                description="获取产品详细规格（材质、尺寸、重量等）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "brand": {
                            "type": "string",
                            "description": f"品牌名称（{'/'.join(supported_brands)}）",
                            "enum": supported_brands,
                        },
                        "url": {
                            "type": "string",
                            "description": "产品页面 URL",
                        },
                    },
                    "required": ["brand", "url"],
                },
            ),
            MCPTool(
                name="search_products",
                description="搜索产品（通过关键词）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "brand": {
                            "type": "string",
                            "description": f"品牌名称（{'/'.join(supported_brands)}）",
                            "enum": supported_brands,
                        },
                        "keyword": {
                            "type": "string",
                            "description": "搜索关键词",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回结果数量",
                            "default": 10,
                        },
                    },
                    "required": ["brand", "keyword"],
                },
            ),
        ]
    
    def get_resources(self) -> List[MCPResource]:
        """获取资源列表"""
        return [
            MCPResource(
                uri="ecommerce://brands",
                name="支持的品牌列表",
                description="获取所有支持的电商品牌",
                mime_type="application/json",
            ),
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """调用工具"""
        logger.info(f"调用工具: {tool_name}, 参数: {arguments}")

        result = None

        if tool_name == "get_product_info":
            result = await self._get_product_info(
                arguments["brand"],
                arguments["url"]
            )

        elif tool_name == "get_product_specs":
            result = await self._get_product_specs(
                arguments["brand"],
                arguments["url"]
            )

        elif tool_name == "search_products":
            result = await self._search_products(
                arguments["brand"],
                arguments["keyword"],
                arguments.get("limit", 10)
            )

        else:
            raise ValueError(f"未知工具: {tool_name}")

        # 将结果转换为 TextContent 列表
        return [TextContent(text=json.dumps(result, ensure_ascii=False, indent=2))]
    
    async def _get_product_info(self, brand: str, url: str) -> Dict[str, Any]:
        """获取产品基本信息"""
        scraper = self.scrapers.get(brand)
        if not scraper:
            raise ValueError(f"不支持的品牌: {brand}")
        
        return await scraper.get_product_info(url)
    
    async def _get_product_specs(self, brand: str, url: str) -> Dict[str, Any]:
        """获取产品详细规格"""
        scraper = self.scrapers.get(brand)
        if not scraper:
            raise ValueError(f"不支持的品牌: {brand}")
        
        return await scraper.get_product_specs(url)
    
    async def _search_products(
        self,
        brand: str,
        keyword: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索产品"""
        scraper = self.scrapers.get(brand)
        if not scraper:
            raise ValueError(f"不支持的品牌: {brand}")
        
        return await scraper.search_products(keyword, limit)

