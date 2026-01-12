"""
Uplift 爬虫实现
"""
from typing import Any, Dict, List

from loguru import logger

from .base import BaseScraper


class UpliftScraper(BaseScraper):
    """
    Uplift 电商爬虫
    
    抓取 Uplift Desk 产品信息
    """
    
    BASE_URL = "https://www.upliftdesk.com"
    
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        """
        获取产品基本信息
        
        Args:
            url: 产品页面 URL
            
        Returns:
            产品信息
        """
        logger.info(f"[Uplift] 获取产品信息: {url}")

        # 获取 HTML（使用 JavaScript 渲染）
        html = await self._fetch_html(url, use_js=True)
        soup = self._parse_html(html)
        
        # 提取信息
        try:
            # 产品标题 - 直接查找第一个 h1
            title_elem = soup.find("h1")
            title = self._clean_text(title_elem.text) if title_elem else "Unknown"

            # 价格 - 从 HTML 中搜索价格模式
            import re
            price_matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', html)
            # 过滤掉小额价格（可能是配件），取合理范围内的最小价格作为起始价
            prices = [float(p.replace(',', '')) for p in price_matches if p]
            # 升降桌价格通常在 $300-$2000 之间
            reasonable_prices = [p for p in prices if 300 <= p <= 2000]
            price = min(reasonable_prices) if reasonable_prices else (max(prices) if prices else 0.0)

            # 描述 - 查找包含产品描述的段落（跳过前几个可能是导航的段落）
            desc_paragraphs = soup.find_all("p")
            description = ""
            for p in desc_paragraphs:
                text = self._clean_text(p.text)
                if len(text) > 50:  # 找到第一个有实质内容的段落
                    description = text
                    break

            # 图片 - 查找产品图片（排除 logo 和小图标）
            img_elem = None
            for img in soup.find_all("img"):
                src = img.get("src", "")
                alt = img.get("alt", "")
                # 排除 logo 和小图标
                if "logo" not in src.lower() and "icon" not in src.lower():
                    if "desk" in alt.lower() or "uplift" in alt.lower():
                        img_elem = img
                        break
            if not img_elem:
                # 如果没找到，取第一个非 logo 图片
                for img in soup.find_all("img"):
                    src = img.get("src", "")
                    if "logo" not in src.lower():
                        img_elem = img
                        break
            image_url = img_elem.get("src") if img_elem else None

            # 评分和评论数 - 暂时设为 None
            rating = None
            review_count = 0
            
            result = {
                "brand": "Uplift",
                "url": url,
                "title": title,
                "price": price,
                "currency": "USD",
                "description": description[:500],  # 限制长度
                "image_url": image_url,
                "rating": rating,
                "review_count": review_count,
                "in_stock": True,  # TODO: 实际检测库存
            }
            
            logger.info(f"[Uplift] 产品信息提取成功: {title}")
            return result
            
        except Exception as e:
            logger.error(f"[Uplift] 提取产品信息失败: {e}")
            return {
                "brand": "Uplift",
                "url": url,
                "error": str(e),
            }
    
    async def get_product_specs(self, url: str) -> Dict[str, Any]:
        """
        获取产品详细规格
        
        Args:
            url: 产品页面 URL
            
        Returns:
            产品规格
        """
        logger.info(f"[Uplift] 获取产品规格: {url}")
        
        # 获取 HTML
        html = await self._fetch_html(url)
        soup = self._parse_html(html)
        
        # 提取规格
        try:
            specs = {}
            
            # 查找规格表
            spec_table = soup.select_one(".specs-table, .product-specs")
            if spec_table:
                rows = spec_table.select("tr")
                for row in rows:
                    cols = row.select("td, th")
                    if len(cols) >= 2:
                        key = self._clean_text(cols[0].text)
                        value = self._clean_text(cols[1].text)
                        specs[key] = value
            
            # 常见规格字段
            common_specs = {
                "material": None,
                "dimensions": None,
                "weight_capacity": None,
                "height_range": None,
                "warranty": None,
            }
            
            # 尝试从规格中提取
            for key, value in specs.items():
                key_lower = key.lower()
                if "material" in key_lower:
                    common_specs["material"] = value
                elif "dimension" in key_lower or "size" in key_lower:
                    common_specs["dimensions"] = value
                elif "weight" in key_lower and "capacity" in key_lower:
                    common_specs["weight_capacity"] = value
                elif "height" in key_lower:
                    common_specs["height_range"] = value
                elif "warranty" in key_lower:
                    common_specs["warranty"] = value
            
            result = {
                "brand": "Uplift",
                "url": url,
                "specs": specs,
                "common_specs": common_specs,
            }
            
            logger.info(f"[Uplift] 规格提取成功，共 {len(specs)} 项")
            return result
            
        except Exception as e:
            logger.error(f"[Uplift] 提取产品规格失败: {e}")
            return {
                "brand": "Uplift",
                "url": url,
                "error": str(e),
            }
    
    async def search_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索产品
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量
            
        Returns:
            产品列表
        """
        logger.info(f"[Uplift] 搜索产品: {keyword}, limit={limit}")
        
        # TODO: 实现搜索功能
        # 这里需要根据 Uplift 网站的实际搜索 API 或页面结构来实现
        
        logger.warning("[Uplift] 搜索功能尚未实现")
        return []

