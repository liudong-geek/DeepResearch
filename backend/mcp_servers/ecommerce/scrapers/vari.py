"""
Vari 爬虫实现
"""
from typing import Any, Dict, List

from loguru import logger

from .base import BaseScraper


class VariScraper(BaseScraper):
    """
    Vari 电商爬虫
    
    抓取 Vari 产品信息
    """
    
    BASE_URL = "https://www.vari.com"
    
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        """获取产品基本信息"""
        logger.info(f"[Vari] 获取产品信息: {url}")

        # 使用 JavaScript 渲染
        html = await self._fetch_html(url, use_js=True)
        soup = self._parse_html(html)

        try:
            import re

            # 产品标题 - 查找第一个 h1
            title_elem = soup.find("h1")
            title = self._clean_text(title_elem.text) if title_elem else "Unknown"

            # 价格 - 从 HTML 中搜索价格模式
            price_matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', html)
            prices = [float(p.replace(',', '')) for p in price_matches if p]
            # 升降桌价格通常在 $300-$2000 之间
            reasonable_prices = [p for p in prices if 300 <= p <= 2000]
            price = min(reasonable_prices) if reasonable_prices else (max(prices) if prices else 0.0)

            # 描述 - 查找有实质内容的段落
            desc_paragraphs = soup.find_all("p")
            description = ""
            for p in desc_paragraphs:
                text = self._clean_text(p.text)
                if len(text) > 50:
                    description = text
                    break

            # 图片 - 查找产品图片
            img_elem = None
            for img in soup.find_all("img"):
                src = img.get("src", "")
                alt = img.get("alt", "")
                if "logo" not in src.lower() and "icon" not in src.lower():
                    if "vari" in alt.lower() or "desk" in alt.lower():
                        img_elem = img
                        break
            if not img_elem:
                for img in soup.find_all("img"):
                    src = img.get("src", "")
                    if "logo" not in src.lower():
                        img_elem = img
                        break
            image_url = img_elem.get("src") if img_elem else None

            result = {
                "brand": "Vari",
                "url": url,
                "title": title,
                "price": price,
                "currency": "USD",
                "description": description[:500],
                "image_url": image_url,
                "rating": None,
                "review_count": 0,
                "in_stock": True,
            }

            logger.info(f"[Vari] 产品信息提取成功: {title}")
            return result

        except Exception as e:
            logger.error(f"[Vari] 提取失败: {e}")
            return {"brand": "Vari", "url": url, "error": str(e)}
    
    async def get_product_specs(self, url: str) -> Dict[str, Any]:
        """获取产品详细规格"""
        logger.info(f"[Vari] 获取产品规格: {url}")
        logger.warning("[Vari] 规格提取尚未实现")
        return {"brand": "Vari", "url": url, "specs": {}}
    
    async def search_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索产品"""
        logger.warning("[Vari] 搜索功能尚未实现")
        return []

