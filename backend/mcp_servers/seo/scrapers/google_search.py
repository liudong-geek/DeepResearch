"""
Google Custom Search API 爬虫
使用 Google Custom Search JSON API（免费配额：100 次/天）
"""
import os
from typing import Any, Dict, List, Optional
import httpx
from loguru import logger

from ...shared.rate_limiter import RateLimiter
from ...shared.cache_manager import CacheManager


class GoogleSearchScraper:
    """Google Custom Search API 爬虫"""

    def __init__(self, rate_limiter: RateLimiter, cache: CacheManager):
        self.rate_limiter = rate_limiter
        self.cache = cache
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"

        if not self.api_key or not self.search_engine_id:
            logger.warning("⚠️ Google Search API 未配置，SEO 功能将受限")

    async def search(
        self,
        query: str,
        market: str = "us",
        num_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        执行 Google 搜索

        Args:
            query: 搜索关键词
            market: 市场（us, uk 等）
            num_results: 返回结果数量（最多 10）

        Returns:
            搜索结果列表
        """
        if not self.api_key or not self.search_engine_id:
            logger.error("❌ Google Search API 未配置")
            return []

        # 检查缓存
        cache_key = f"google_search:{query}:{market}:{num_results}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"✅ 缓存命中: {query}")
            return cached

        # 限速
        await self.rate_limiter.acquire()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "key": self.api_key,
                    "cx": self.search_engine_id,
                    "q": query,
                    "gl": market,  # 地理位置
                    "num": min(num_results, 10),  # 最多 10 个结果
                }

                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                # 解析结果
                results = []
                for item in data.get("items", []):
                    results.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "displayLink": item.get("displayLink"),
                        "position": len(results) + 1,
                        "_source": {
                            "type": "google_search",
                            "url": item.get("link"),
                            "query": query,
                            "market": market,
                        }
                    })

                # 缓存结果（7 天）
                self.cache.set(cache_key, results)

                logger.info(f"✅ Google 搜索成功: {query} ({len(results)} 个结果)")
                return results

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("❌ Google Search API 配额已用完（100 次/天）")
            else:
                logger.error(f"❌ Google Search API 错误: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Google 搜索失败: {e}")
            return []

    async def get_serp_features(self, query: str, market: str = "us") -> Dict[str, Any]:
        """
        获取 SERP 特性（Featured Snippet, People Also Ask 等）

        注意：Google Custom Search API 不直接提供这些数据
        这里返回搜索结果的元数据作为替代
        """
        results = await self.search(query, market, num_results=10)

        if not results:
            return {
                "query": query,
                "market": market,
                "featured_snippet": None,
                "people_also_ask": [],
                "top_results": [],
            }

        # 提取前 3 个结果作为 top_results
        top_results = results[:3]

        return {
            "query": query,
            "market": market,
            "featured_snippet": None,  # Custom Search API 不提供
            "people_also_ask": [],  # Custom Search API 不提供
            "top_results": [
                {
                    "title": r["title"],
                    "url": r["link"],
                    "snippet": r["snippet"],
                    "position": r["position"],
                }
                for r in top_results
            ],
            "total_results": len(results),
            "_source": {
                "type": "serp_features",
                "query": query,
                "market": market,
            }
        }

    async def analyze_competitor_rankings(
        self,
        keyword: str,
        competitors: List[str],
        market: str = "us"
    ) -> Dict[str, Any]:
        """
        分析竞品在搜索结果中的排名

        Args:
            keyword: 搜索关键词
            competitors: 竞品品牌列表
            market: 市场

        Returns:
            竞品排名分析
        """
        results = await self.search(keyword, market, num_results=10)

        if not results:
            return {
                "keyword": keyword,
                "market": market,
                "rankings": {},
                "insights": "无搜索结果数据",
            }

        # 分析每个竞品的排名
        rankings = {}
        for competitor in competitors:
            competitor_lower = competitor.lower()
            for result in results:
                title_lower = result["title"].lower()
                link_lower = result["link"].lower()

                if competitor_lower in title_lower or competitor_lower in link_lower:
                    rankings[competitor] = {
                        "position": result["position"],
                        "title": result["title"],
                        "url": result["link"],
                        "snippet": result["snippet"],
                    }
                    break

        return {
            "keyword": keyword,
            "market": market,
            "rankings": rankings,
            "insights": f"找到 {len(rankings)}/{len(competitors)} 个竞品在前 10 名",
            "_source": {
                "type": "competitor_rankings",
                "keyword": keyword,
                "market": market,
            }
        }

