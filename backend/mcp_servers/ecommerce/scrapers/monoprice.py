"""
Monoprice 爬虫（专用，处理 Cloudflare）
"""
from typing import Any, Dict
from datetime import datetime

from loguru import logger

from .base import BaseScraper


class MonopriceScraper(BaseScraper):
    """
    Monoprice 爬虫
    
    特点：
    - 使用 Cloudflare 保护
    - 需要更长的等待时间
    - 需要模拟真实用户行为
    """
    
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        """
        获取 Monoprice 产品信息
        
        Args:
            url: 产品页面 URL
            
        Returns:
            产品信息字典
        """
        logger.info(f"[Monoprice] 获取产品信息: {url}")
        
        try:
            # 使用 JavaScript 渲染（Monoprice 需要 JS）
            html = await self._fetch_html(url, use_js=True)
            soup = self._parse_html(html)
            
            # 检查是否仍然被 Cloudflare 拦截
            if any(keyword in html for keyword in [
                "Verify you are human",
                "cf-browser-verification",
                "challenge-platform"
            ]):
                logger.error("[Monoprice] Cloudflare 挑战未通过")
                return {
                    "error": "Cloudflare protection detected",
                    "brand": "Monoprice",
                    "url": url,
                }
            
            # 提取产品信息
            title = self._extract_title(soup)
            price = self._extract_price(soup)
            description = self._extract_description(soup)
            image_url = self._extract_image(soup, url)
            
            result = {
                "title": title,
                "price": price,
                "description": description,
                "image_url": image_url,
                "url": url,
                "brand": "Monoprice",
                "_source": {
                    "type": "product_page",
                    "url": url,
                    "brand": "Monoprice",
                    "extracted_at": datetime.now().isoformat(),
                    "data_points": ["title", "price", "description", "image"],
                }
            }
            
            logger.info(f"[Monoprice] 产品信息提取成功: {title}")
            return result
            
        except Exception as e:
            logger.error(f"[Monoprice] 获取产品信息失败: {e}")
            return {
                "error": str(e),
                "brand": "Monoprice",
                "url": url,
            }
    
    def _extract_title(self, soup) -> str:
        """提取产品标题"""
        # Monoprice 特定的选择器
        selectors = [
            "h1.product-name",
            "h1[itemprop='name']",
            ".product-title h1",
            "h1",
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                title = self._clean_text(elem.text)
                if title and len(title) > 5:
                    return title
        
        return "Unknown Product"
    
    def _extract_price(self, soup) -> float:
        """提取产品价格"""
        # Monoprice 特定的选择器
        selectors = [
            ".price-box .price",
            "[itemprop='price']",
            ".product-price",
            ".regular-price",
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                price_text = elem.get("content") or elem.text
                price = self._parse_price(price_text)
                if price > 0:
                    return price
        
        return 0.0
    
    def _extract_description(self, soup) -> str:
        """提取产品描述"""
        # Monoprice 特定的选择器
        selectors = [
            ".product-description",
            "#product-description",
            ".std",
            "[itemprop='description']",
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                desc = self._clean_text(elem.text)
                if desc and len(desc) > 50:
                    return desc
        
        return ""
    
    def _extract_image(self, soup, base_url: str) -> str:
        """提取产品图片"""
        # Monoprice 特定的选择器
        selectors = [
            ".product-image img",
            "#image-main",
            "[itemprop='image']",
            ".gallery img",
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img:
                src = img.get("src") or img.get("data-src")
                if src and "logo" not in src.lower():
                    return self._make_absolute_url(src, base_url)
        
        return None

