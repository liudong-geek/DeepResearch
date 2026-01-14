"""
Reddit 内容爬虫实现
"""
from typing import Any, Dict, List
import httpx
import random

from loguru import logger

from .base import BaseContentScraper


class RedditContentScraper(BaseContentScraper):
    """
    Reddit 内容爬虫

    抓取 Reddit 子版块的帖子和评论内容

    使用 Reddit JSON API（无需认证）:
    - 子版块: https://www.reddit.com/r/subreddit/hot.json
    - 搜索: https://www.reddit.com/search.json?q=keyword

    优点:
    - 无需申请 Reddit API
    - 无需配置 Client ID/Secret
    - 简单易用

    注意:
    - 可能遇到 403 错误（反爬虫）
    - 请求频率限制较严格
    - 建议配置 Reddit API 以获得更好的稳定性
    """

    BASE_URL = "https://www.reddit.com"

    # User-Agent 池（模拟不同浏览器）
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    async def get_content(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        获取 Reddit 内容列表
        
        Args:
            query: 子版块名称（如 "r/StandingDesk"）或搜索关键词
            limit: 返回内容数量
            
        Returns:
            内容列表
        """
        logger.info(f"[Reddit Content] 获取内容: {query}, limit={limit}")
        
        try:
            # 判断是子版块还是搜索关键词
            if query.startswith("r/"):
                # 子版块
                subreddit = query[2:]
                url = f"{self.BASE_URL}/r/{subreddit}/hot.json?limit={limit}"
            else:
                # 搜索关键词
                url = f"{self.BASE_URL}/search.json?q={query}&limit={limit}&sort=relevance"
            
            # 随机选择 User-Agent（模拟不同浏览器）
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
            }

            # 限速
            await self.rate_limiter.acquire()

            # 添加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, headers=headers, timeout=30.0, follow_redirects=True)
                        response.raise_for_status()
                        data = response.json()
                        break  # 成功，跳出重试循环
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 403:
                        logger.warning(f"[Reddit Content] 遇到 403 错误（尝试 {attempt + 1}/{max_retries}）")
                        if attempt < max_retries - 1:
                            # 等待后重试
                            import asyncio
                            await asyncio.sleep(2 ** attempt)  # 指数退避
                            continue
                        else:
                            logger.error(f"[Reddit Content] 403 错误，建议配置 Reddit API")
                            return {
                                "source": "reddit",
                                "query": query,
                                "total": 0,
                                "contents": [],
                                "error": "403 Forbidden - 建议配置 Reddit API 以获得更好的稳定性",
                            }
                    raise
            
            # 解析 Reddit JSON 响应
            posts = []
            
            if "data" in data and "children" in data["data"]:
                for item in data["data"]["children"]:
                    post_data = item.get("data", {})
                    
                    # 提取帖子信息
                    post = {
                        "id": post_data.get("id"),
                        "title": post_data.get("title", ""),
                        "content": post_data.get("selftext", ""),
                        "author": post_data.get("author", ""),
                        "score": post_data.get("score", 0),
                        "num_comments": post_data.get("num_comments", 0),
                        "created_utc": post_data.get("created_utc", 0),
                        "url": f"{self.BASE_URL}{post_data.get('permalink', '')}",
                        "subreddit": post_data.get("subreddit", ""),
                        "type": "reddit_post",
                    }
                    
                    posts.append(post)
            
            logger.info(f"[Reddit Content] 获取成功，共 {len(posts)} 个帖子")
            
            return {
                "source": "reddit",
                "query": query,
                "total": len(posts),
                "contents": posts,
            }
            
        except Exception as e:
            logger.error(f"[Reddit Content] 获取内容失败: {e}")
            return {
                "source": "reddit",
                "query": query,
                "error": str(e),
                "contents": [],
            }
    
    async def extract_article(
        self,
        url: str
    ) -> Dict[str, Any]:
        """
        提取 Reddit 帖子详细内容（包括评论）
        
        Args:
            url: Reddit 帖子 URL
            
        Returns:
            帖子详细内容
        """
        logger.info(f"[Reddit Content] 提取帖子: {url}")
        
        try:
            # 转换为 JSON API URL
            json_url = url.rstrip('/') + '.json'
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            }
            
            # 限速
            await self.rate_limiter.acquire()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(json_url, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            
            # 解析帖子和评论
            if not data or len(data) < 2:
                raise ValueError("Invalid Reddit response")
            
            # 帖子数据
            post_data = data[0]["data"]["children"][0]["data"]
            
            # 评论数据
            comments = []
            if len(data) > 1 and "data" in data[1]:
                comments = self._extract_comments(data[1]["data"]["children"])
            
            result = {
                "source": "reddit",
                "type": "reddit_post",
                "url": url,
                "title": post_data.get("title", ""),
                "content": post_data.get("selftext", ""),
                "author": post_data.get("author", ""),
                "score": post_data.get("score", 0),
                "num_comments": post_data.get("num_comments", 0),
                "created_utc": post_data.get("created_utc", 0),
                "subreddit": post_data.get("subreddit", ""),
                "comments": comments[:20],  # 限制评论数量
            }

            logger.info(f"[Reddit Content] 提取成功，{len(comments)} 条评论")
            return result

        except Exception as e:
            logger.error(f"[Reddit Content] 提取帖子失败: {e}")
            return {
                "source": "reddit",
                "type": "reddit_post",
                "url": url,
                "error": str(e),
            }

    def _extract_comments(self, comment_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取评论"""
        comments = []

        for item in comment_data:
            if item.get("kind") != "t1":  # t1 是评论类型
                continue

            data = item.get("data", {})

            # 跳过 "more" 类型的占位符
            if data.get("body") in ["[deleted]", "[removed]", None]:
                continue

            comment = {
                "author": data.get("author", ""),
                "body": data.get("body", ""),
                "score": data.get("score", 0),
                "created_utc": data.get("created_utc", 0),
            }

            comments.append(comment)

        return comments

