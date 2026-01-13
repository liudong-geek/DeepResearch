"""
Reddit 评论/讨论爬虫实现
"""
from typing import Any, Dict, List
from collections import Counter
import re
from bs4 import BeautifulSoup

from loguru import logger

from .base import BaseReviewScraper


class RedditReviewScraper(BaseReviewScraper):
    """
    Reddit 讨论爬虫
    
    抓取 Reddit 子版块的讨论和评论
    """
    
    BASE_URL = "https://www.reddit.com"
    
    async def get_reviews(
        self,
        product_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取 Reddit 讨论列表
        
        Args:
            product_id: 子版块名称（如 "StandingDesk"）或搜索关键词
            limit: 返回讨论数量
            
        Returns:
            讨论列表
        """
        logger.info(f"[Reddit] 获取讨论: {product_id}, limit={limit}")
        
        try:
            # 判断是子版块还是搜索关键词
            if product_id.startswith("r/"):
                # 子版块
                subreddit = product_id[2:]
                url = f"{self.BASE_URL}/r/{subreddit}/hot.json?limit={limit}"
            else:
                # 搜索关键词
                url = f"{self.BASE_URL}/search.json?q={product_id}&limit={limit}&sort=relevance"
            
            # 使用 Reddit JSON API
            import httpx
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            }
            
            # 限速
            await self.rate_limiter.acquire()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            
            # 解析 Reddit JSON 响应
            posts = []
            
            if "data" in data and "children" in data["data"]:
                for item in data["data"]["children"]:
                    post_data = item.get("data", {})
                    
                    # 提取帖子信息
                    post = {
                        "id": post_data.get("id"),
                        "title": post_data.get("title", ""),
                        "text": post_data.get("selftext", ""),
                        "author": post_data.get("author", ""),
                        "score": post_data.get("score", 0),
                        "num_comments": post_data.get("num_comments", 0),
                        "created_utc": post_data.get("created_utc", 0),
                        "url": f"{self.BASE_URL}{post_data.get('permalink', '')}",
                        "subreddit": post_data.get("subreddit", ""),
                    }
                    
                    posts.append(post)
            
            logger.info(f"[Reddit] 获取成功，共 {len(posts)} 个讨论")
            
            return {
                "platform": "reddit",
                "product_id": product_id,
                "total": len(posts),
                "reviews": posts,
            }
            
        except Exception as e:
            logger.error(f"[Reddit] 获取讨论失败: {e}")
            return {
                "platform": "reddit",
                "product_id": product_id,
                "error": str(e),
                "reviews": [],
            }
    
    async def analyze_reviews(
        self,
        product_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        分析 Reddit 讨论
        
        Args:
            product_id: 子版块名称或搜索关键词
            limit: 分析讨论数量
            
        Returns:
            分析结果
        """
        logger.info(f"[Reddit] 分析讨论: {product_id}, limit={limit}")
        
        # 获取讨论
        posts_data = await self.get_reviews(product_id, limit)
        posts = posts_data["reviews"]
        
        # 分析讨论
        analysis = self._analyze_posts(posts)
        
        result = {
            "platform": "reddit",
            "product_id": product_id,
            "total_analyzed": len(posts),
            "analysis": analysis,
        }
        
        logger.info(f"[Reddit] 分析完成，提取 {len(analysis['topics'])} 个主题")
        return result
    
    def _analyze_posts(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析讨论列表"""
        # 提取主题
        topics = self._extract_topics_from_posts(posts)
        
        # 情感分析（基于评分）
        sentiment = self._analyze_sentiment_from_posts(posts)
        
        # 热门讨论
        top_posts = sorted(posts, key=lambda x: x.get("score", 0), reverse=True)[:5]
        
        return {
            "topics": topics,
            "sentiment": sentiment,
            "top_posts": top_posts,
        }

    def _extract_topics_from_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从讨论中提取主题"""
        keywords = []

        # 升降桌相关关键词
        topic_keywords = {
            "stability": ["stable", "stability", "wobble", "wobbly", "shake"],
            "price": ["price", "expensive", "cheap", "cost", "budget", "worth"],
            "quality": ["quality", "build", "construction", "material"],
            "assembly": ["assembly", "install", "setup", "easy", "difficult"],
            "motor": ["motor", "noise", "quiet", "loud", "smooth"],
            "height": ["height", "range", "tall", "short", "adjust"],
            "desktop": ["desktop", "top", "surface", "laminate", "bamboo"],
            "brand": ["uplift", "jarvis", "flexispot", "autonomous", "vari"],
            "recommendation": ["recommend", "suggest", "advice", "opinion"],
            "comparison": ["vs", "versus", "compare", "better", "best"],
        }

        for post in posts:
            text = (post.get("title", "") + " " + post.get("text", "")).lower()

            for topic, keywords_list in topic_keywords.items():
                if any(kw in text for kw in keywords_list):
                    keywords.append(topic)

        # 统计频率
        counter = Counter(keywords)

        # 返回 Top 10
        topics = [
            {"topic": topic, "count": count, "percentage": round(count / len(posts) * 100, 2)}
            for topic, count in counter.most_common(10)
        ]

        return topics

    def _analyze_sentiment_from_posts(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析讨论情感（基于评分和关键词）"""
        if not posts:
            return {
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "neutral_percentage": 0.0,
                "average_score": 0.0,
            }

        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_score = 0

        # 正面和负面关键词
        positive_keywords = [
            "great", "excellent", "amazing", "love", "perfect", "best",
            "recommend", "happy", "satisfied", "solid", "sturdy", "stable"
        ]

        negative_keywords = [
            "bad", "terrible", "awful", "hate", "worst", "poor",
            "disappointed", "waste", "broken", "unstable", "wobble", "regret"
        ]

        for post in posts:
            score = post.get("score", 0)
            text = (post.get("title", "") + " " + post.get("text", "")).lower()

            total_score += score

            # 基于评分和关键词的情感分类
            positive_score = sum(1 for kw in positive_keywords if kw in text)
            negative_score = sum(1 for kw in negative_keywords if kw in text)

            # 综合评分和关键词
            if score > 10 or positive_score > negative_score:
                positive_count += 1
            elif score < 0 or negative_score > positive_score:
                negative_count += 1
            else:
                neutral_count += 1

        total = len(posts)
        average_score = total_score / total if total > 0 else 0

        return {
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_percentage": round(positive_count / total * 100, 2) if total > 0 else 0,
            "negative_percentage": round(negative_count / total * 100, 2) if total > 0 else 0,
            "neutral_percentage": round(neutral_count / total * 100, 2) if total > 0 else 0,
            "average_score": round(average_score, 2),
            "total_posts": total,
        }

