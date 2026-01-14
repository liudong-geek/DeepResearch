"""
Trustpilot 评论爬虫实现
"""
from typing import Any, Dict, List, Optional
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser

from loguru import logger

from .base import BaseReviewScraper


class TrustpilotReviewScraper(BaseReviewScraper):
    """
    Trustpilot 评论爬虫

    抓取 Trustpilot 产品评论（无需登录）
    """

    BASE_URL = "https://www.trustpilot.com"

    def __init__(self, rate_limiter, cache):
        super().__init__(rate_limiter, cache)
        self._browser: Optional[Browser] = None
    
    async def get_reviews(
        self,
        company_domain: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取 Trustpilot 评论列表
        
        Args:
            company_domain: 公司域名（如 "flexispot.com"）
            limit: 返回评论数量
            
        Returns:
            评论列表
        """
        logger.info(f"[Trustpilot] 获取评论: {company_domain}, limit={limit}")
        
        try:
            # 构建评论页面 URL
            reviews_url = f"{self.BASE_URL}/review/{company_domain}"
            
            # 获取 HTML
            html = await self._fetch_html(reviews_url)
            
            # 解析评论
            reviews = self._parse_reviews(html, limit)
            
            # 解析公司信息
            company_info = self._parse_company_info(html)
            
            result = {
                "platform": "trustpilot",
                "company_domain": company_domain,
                "company_name": company_info.get("name", company_domain),
                "overall_rating": company_info.get("rating", 0),
                "total_reviews": company_info.get("total_reviews", 0),
                "reviews": reviews,
                "source_url": reviews_url,
            }
            
            logger.info(f"[Trustpilot] 获取到 {len(reviews)} 条评论")
            return result
            
        except Exception as e:
            logger.error(f"[Trustpilot] 获取评论失败: {e}")
            return {
                "platform": "trustpilot",
                "company_domain": company_domain,
                "error": str(e),
                "reviews": [],
            }
    
    async def analyze_reviews(
        self,
        company_domain: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        分析 Trustpilot 评论
        
        Args:
            company_domain: 公司域名
            limit: 分析评论数量
            
        Returns:
            分析结果（基础统计，详细分析由 LLM 完成）
        """
        logger.info(f"[Trustpilot] 分析评论: {company_domain}, limit={limit}")
        
        # 获取评论
        reviews_data = await self.get_reviews(company_domain, limit)
        reviews = reviews_data.get("reviews", [])
        
        # 基础统计分析
        analysis = self._analyze_review_list(reviews)
        
        result = {
            "platform": "trustpilot",
            "company_domain": company_domain,
            "company_name": reviews_data.get("company_name", company_domain),
            "overall_rating": reviews_data.get("overall_rating", 0),
            "total_analyzed": len(reviews),
            "analysis": analysis,
        }
        
        logger.info(f"[Trustpilot] 分析完成")
        return result
    
    async def _fetch_html(self, url: str) -> str:
        """使用 Playwright 获取渲染后的 HTML"""
        # 限速
        await self.rate_limiter.acquire()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # 访问页面
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # 等待评论加载 - 使用正确的选择器
                await page.wait_for_selector('article[data-service-review-card-paper]', timeout=10000)

                # 获取 HTML
                html = await page.content()

                return html
            finally:
                await browser.close()
    
    def _parse_company_info(self, html: str) -> Dict[str, Any]:
        """解析公司信息"""
        soup = BeautifulSoup(html, "html.parser")
        
        info = {}
        
        # 公司名称
        name_elem = soup.find("span", class_=re.compile(r"title.*title"))
        if name_elem:
            info["name"] = self._clean_text(name_elem.get_text())
        
        # 总评分
        rating_elem = soup.find("p", class_=re.compile(r"typography.*heading"))
        if rating_elem:
            rating_text = self._clean_text(rating_elem.get_text())
            try:
                info["rating"] = float(rating_text)
            except:
                pass
        
        # 总评论数
        count_elem = soup.find("p", class_=re.compile(r"typography.*regular"), string=re.compile(r"reviews"))
        if count_elem:
            count_text = self._clean_text(count_elem.get_text())
            # 提取数字（如 "1,234 reviews" -> 1234）
            numbers = re.findall(r'[\d,]+', count_text)
            if numbers:
                try:
                    info["total_reviews"] = int(numbers[0].replace(',', ''))
                except:
                    pass
        
        return info

    def _parse_reviews(self, html: str, limit: int) -> List[Dict[str, Any]]:
        """解析评论列表"""
        soup = BeautifulSoup(html, "html.parser")
        reviews = []

        # 查找所有评论卡片 - 使用正确的选择器
        review_cards = soup.find_all("article", {"data-service-review-card-paper": True})

        logger.info(f"找到 {len(review_cards)} 个评论卡片")

        for card in review_cards[:limit]:
            try:
                review = self._parse_review_card(card)
                if review:
                    reviews.append(review)
            except Exception as e:
                logger.warning(f"解析评论卡片失败: {e}")
                continue

        return reviews

    def _parse_review_card(self, card) -> Dict[str, Any]:
        """解析单个评论卡片"""
        review = {}

        # 评分（1-5星）- 从 img alt 属性中提取
        rating_img = card.find("img", alt=re.compile(r"Rated \d out of 5 stars"))
        if rating_img:
            alt_text = rating_img.get("alt", "")
            # 提取 "Rated X out of 5 stars" 中的 X
            match = re.search(r"Rated (\d) out of 5 stars", alt_text)
            if match:
                try:
                    review["rating"] = int(match.group(1))
                except:
                    review["rating"] = 0

        # 如果没有找到评分，尝试从 src 中提取
        if "rating" not in review:
            rating_img = card.find("img", src=re.compile(r"stars-(\d)\.svg"))
            if rating_img:
                src = rating_img.get("src", "")
                match = re.search(r"stars-(\d)\.svg", src)
                if match:
                    try:
                        review["rating"] = int(match.group(1))
                    except:
                        review["rating"] = 0

        # 标题 - 查找 h2 标签
        title_elem = card.find("h2")
        if title_elem:
            review["title"] = self._clean_text(title_elem.get_text())

        # 评论文本 - 尝试多种选择器
        text_elem = card.find("p", {"data-relevant-review-text-typography": True})
        if not text_elem:
            text_elem = card.find("p", {"data-service-review-text-typography": True})
        if text_elem:
            review["text"] = self._clean_text(text_elem.get_text())

        # 作者 - 使用 data-consumer-name-typography 属性
        author_elem = card.find("span", {"data-consumer-name-typography": True})
        if author_elem:
            review["author"] = self._clean_text(author_elem.get_text())

        # 日期
        date_elem = card.find("time")
        if date_elem:
            review["date"] = date_elem.get("datetime", "")
            review["date_display"] = self._clean_text(date_elem.get_text())

        # 验证购买 - 查找 verified 标记
        verified_elem = card.find(attrs={"data-service-review-verified-badge": True})
        review["verified"] = verified_elem is not None

        return review

    def _analyze_review_list(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基础统计分析"""
        if not reviews:
            return {
                "sentiment": {},
                "rating_distribution": {},
            }

        # 评分分布
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating = review.get("rating", 0)
            if rating in rating_counts:
                rating_counts[rating] += 1

        # 情感分析（基于评分）
        positive = rating_counts[4] + rating_counts[5]
        negative = rating_counts[1] + rating_counts[2]
        neutral = rating_counts[3]
        total = len(reviews)

        sentiment = {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_percentage": round(positive / total * 100, 1) if total > 0 else 0,
            "negative_percentage": round(negative / total * 100, 1) if total > 0 else 0,
        }

        return {
            "sentiment": sentiment,
            "rating_distribution": rating_counts,
            "average_rating": sum(r.get("rating", 0) for r in reviews) / total if total > 0 else 0,
        }

