"""
Amazon 评论爬虫实现
"""
from typing import Any, Dict, List, Optional
from collections import Counter
import re
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page

from loguru import logger

from .base import BaseReviewScraper


class AmazonReviewScraper(BaseReviewScraper):
    """
    Amazon 评论爬虫

    使用 Playwright 抓取 Amazon 产品评论
    """

    BASE_URL = "https://www.amazon.com"

    def __init__(self, rate_limiter, cache):
        super().__init__(rate_limiter, cache)
        self._browser: Optional[Browser] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def get_reviews(
        self,
        product_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取评论列表

        Args:
            product_id: 产品 ASIN
            limit: 返回评论数量

        Returns:
            评论列表
        """
        logger.info(f"[Amazon] 获取评论: {product_id}, limit={limit}")

        try:
            # 构建评论页面 URL
            reviews_url = f"{self.BASE_URL}/product-reviews/{product_id}/ref=cm_cr_dp_d_show_all_btm"

            # 获取 HTML
            html = await self._fetch_html_with_playwright(reviews_url)

            # 解析评论
            reviews = self._parse_reviews(html, limit)

            result = {
                "platform": "amazon",
                "product_id": product_id,
                "total_reviews": len(reviews),
                "reviews": reviews,
                "source_url": reviews_url,
            }

            logger.info(f"[Amazon] 获取到 {len(reviews)} 条评论")
            return result

        except Exception as e:
            logger.error(f"[Amazon] 获取评论失败: {e}")
            return {
                "platform": "amazon",
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
        分析评论

        Args:
            product_id: 产品 ASIN
            limit: 分析评论数量

        Returns:
            分析结果
        """
        logger.info(f"[Amazon] 分析评论: {product_id}, limit={limit}")

        # 获取评论
        reviews_data = await self.get_reviews(product_id, limit)
        reviews = reviews_data["reviews"]

        # 分析评论
        analysis = self._analyze_review_list(reviews)

        result = {
            "platform": "amazon",
            "product_id": product_id,
            "total_analyzed": len(reviews),
            "analysis": analysis,
        }

        logger.info(f"[Amazon] 分析完成，提取 {len(analysis['topics'])} 个主题")
        return result

    def _analyze_review_list(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析评论列表

        Args:
            reviews: 评论列表

        Returns:
            分析结果
        """
        # 提取主题标签
        topics = self._extract_topics(reviews)

        # 情感分析
        sentiment = self._analyze_sentiment(reviews)

        # 提取典型评论
        typical_reviews = self._extract_typical_reviews(reviews)

        return {
            "topics": topics,
            "sentiment": sentiment,
            "typical_reviews": typical_reviews,
        }

    def _extract_topics(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取主题标签"""
        # 简单的关键词提取
        keywords = []
        for review in reviews:
            text = review.get("text", "").lower()
            # 提取常见主题词
            if "stable" in text or "stability" in text:
                keywords.append("stability")
            if "wobble" in text or "wobbly" in text:
                keywords.append("wobble")
            if "quality" in text:
                keywords.append("quality")
            if "price" in text or "expensive" in text or "cheap" in text:
                keywords.append("price")
            if "assembly" in text or "install" in text:
                keywords.append("assembly")
            if "motor" in text or "noise" in text:
                keywords.append("motor_noise")
            if "height" in text or "range" in text:
                keywords.append("height_range")
            if "desk" in text and "top" in text:
                keywords.append("desktop")

        # 统计频率
        counter = Counter(keywords)

        # 返回 Top 10
        topics = [
            {"topic": topic, "count": count, "percentage": count / len(reviews) * 100}
            for topic, count in counter.most_common(10)
        ]

        return topics

    def _analyze_sentiment(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        情感分析

        基于评分和关键词进行简单的情感分析
        """
        if not reviews:
            return {
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "neutral_percentage": 0.0,
                "average_rating": 0.0,
            }

        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_rating = 0

        # 正面和负面关键词
        positive_keywords = [
            "great", "excellent", "amazing", "love", "perfect", "best",
            "fantastic", "wonderful", "awesome", "solid", "sturdy", "stable",
            "recommend", "happy", "satisfied", "quality", "worth"
        ]

        negative_keywords = [
            "bad", "terrible", "awful", "hate", "worst", "poor",
            "disappointed", "waste", "broken", "defective", "unstable",
            "wobble", "cheap", "flimsy", "regret", "return"
        ]

        for review in reviews:
            rating = review.get("rating", 0)
            text = review.get("text", "").lower()

            total_rating += rating

            # 基于评分的情感分类
            if rating >= 4:
                positive_count += 1
            elif rating <= 2:
                negative_count += 1
            else:
                # 对于中性评分（3星），使用关键词分析
                positive_score = sum(1 for kw in positive_keywords if kw in text)
                negative_score = sum(1 for kw in negative_keywords if kw in text)

                if positive_score > negative_score:
                    positive_count += 1
                elif negative_score > positive_score:
                    negative_count += 1
                else:
                    neutral_count += 1

        total = len(reviews)
        average_rating = total_rating / total if total > 0 else 0

        return {
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_percentage": round(positive_count / total * 100, 2) if total > 0 else 0,
            "negative_percentage": round(negative_count / total * 100, 2) if total > 0 else 0,
            "neutral_percentage": round(neutral_count / total * 100, 2) if total > 0 else 0,
            "average_rating": round(average_rating, 2),
            "total_reviews": total,
        }

    def _extract_typical_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """提取典型评论"""
        # 按评分分组
        positive_reviews = [r for r in reviews if r.get("rating", 0) >= 4]
        negative_reviews = [r for r in reviews if r.get("rating", 0) <= 2]

        # 取前 5 条
        return {
            "positive": positive_reviews[:5],
            "negative": negative_reviews[:5],
        }

    async def _get_browser(self) -> Browser:
        """获取或创建浏览器实例"""
        if self._browser is None:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=True)
            logger.debug("Playwright 浏览器已启动（Review）")
        return self._browser

    async def _close_browser(self):
        """关闭浏览器"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            logger.debug("Playwright 浏览器已关闭（Review）")

    async def _fetch_html_with_playwright(self, url: str) -> str:
        """使用 Playwright 获取 HTML"""
        # 检查缓存
        cache_key = f"review:html:{url}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"HTML 缓存命中: {url}")
            return cached

        # 限速
        await self.rate_limiter.acquire()

        logger.info(f"正在抓取评论页面: {url}")

        browser = await self._get_browser()
        page = await browser.new_page()

        try:
            # 设置 User-Agent
            await page.set_extra_http_headers(self.headers)

            # 访问页面
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # 等待评论加载
            await page.wait_for_timeout(3000)

            # 获取 HTML
            html = await page.content()

            # 存入缓存
            self.cache.set(cache_key, html)

            return html
        finally:
            await page.close()

    def _parse_reviews(self, html: str, limit: int) -> List[Dict[str, Any]]:
        """解析评论 HTML"""
        soup = BeautifulSoup(html, "html.parser")
        reviews = []

        # 查找评论容器
        review_divs = soup.find_all("div", {"data-hook": "review"})

        logger.info(f"找到 {len(review_divs)} 个评论元素")

        for review_div in review_divs[:limit]:
            try:
                # 评分
                rating_elem = review_div.find("i", {"data-hook": "review-star-rating"})
                rating = 0
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    match = re.search(r"(\d+\.?\d*)", rating_text)
                    if match:
                        rating = float(match.group(1))

                # 标题
                title_elem = review_div.find("a", {"data-hook": "review-title"})
                title = self._clean_text(title_elem.get_text()) if title_elem else ""

                # 评论文本
                text_elem = review_div.find("span", {"data-hook": "review-body"})
                text = self._clean_text(text_elem.get_text()) if text_elem else ""

                # 作者
                author_elem = review_div.find("span", class_="a-profile-name")
                author = self._clean_text(author_elem.get_text()) if author_elem else "Anonymous"

                # 日期
                date_elem = review_div.find("span", {"data-hook": "review-date"})
                date = self._clean_text(date_elem.get_text()) if date_elem else ""

                # 验证购买
                verified_elem = review_div.find("span", {"data-hook": "avp-badge"})
                verified = verified_elem is not None

                # 评论 ID
                review_id = review_div.get("id", "")

                reviews.append({
                    "id": review_id,
                    "rating": rating,
                    "title": title,
                    "text": text,
                    "author": author,
                    "date": date,
                    "verified": verified,
                })

            except Exception as e:
                logger.warning(f"解析评论失败: {e}")
                continue

        logger.info(f"成功解析 {len(reviews)} 条评论")
        return reviews

    def _analyze_sentiment(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """情感分析"""
        positive = sum(1 for r in reviews if r.get("rating", 0) >= 4)
        negative = sum(1 for r in reviews if r.get("rating", 0) <= 2)
        neutral = len(reviews) - positive - negative

        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_percentage": positive / len(reviews) * 100 if reviews else 0,
            "negative_percentage": negative / len(reviews) * 100 if reviews else 0,
        }

