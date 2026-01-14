"""
Jarvis 爬虫实现
"""
from typing import Any, Dict, List

from loguru import logger

from .base import BaseScraper


class JarvisScraper(BaseScraper):
    """
    Jarvis 电商爬虫
    
    抓取 Fully Jarvis 产品信息
    """
    
    BASE_URL = "https://www.fully.com"
    
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        """获取产品基本信息"""
        logger.info(f"[Jarvis] 获取产品信息: {url}")

        # 使用 JavaScript 渲染
        html = await self._fetch_html(url, use_js=True)
        soup = self._parse_html(html)

        try:
            import re

            # 产品标题 - 查找第一个 h1
            title_elem = soup.find("h1")
            title = self._clean_text(title_elem.text) if title_elem else "Unknown"

            # 价格提取 - 多种策略
            import json as json_lib
            price = 0.0
            price_source = "unknown"

            # 策略 1: 从 JSON-LD 结构化数据中提取
            try:
                json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
                json_ld_matches = re.findall(json_ld_pattern, html, re.DOTALL | re.IGNORECASE)
                for json_str in json_ld_matches:
                    try:
                        data = json_lib.loads(json_str)
                        items = [data] if isinstance(data, dict) else data
                        for item in items:
                            if item.get('@type') == 'Product' and 'offers' in item:
                                offers = item['offers']
                                if isinstance(offers, dict):
                                    price_value = offers.get('price') or offers.get('lowPrice')
                                    if price_value:
                                        price = float(price_value)
                                        price_source = "json-ld"
                                        logger.info(f"[Jarvis] 从 JSON-LD 提取价格: ${price}")
                                        break
                        if price > 0:
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"[Jarvis] JSON-LD 提取失败: {e}")

            # 策略 2: 从 JavaScript 变量中提取
            if price == 0.0:
                try:
                    js_price_patterns = [
                        r'"price":\s*(\d+(?:\.\d{2})?)',
                        r'price:\s*(\d+(?:\.\d{2})?)',
                        r'data-price="(\d+(?:\.\d{2})?)"',
                        r'"lowPrice":\s*(\d+(?:\.\d{2})?)',
                    ]
                    for pattern in js_price_patterns:
                        matches = re.findall(pattern, html)
                        if matches:
                            # 过滤合理价格（$400-$3000 for standing desks）
                            valid_prices = [float(m) for m in matches if 400 <= float(m) <= 3000]
                            if valid_prices:
                                price = min(valid_prices)
                                price_source = "javascript"
                                logger.info(f"[Jarvis] 从 JavaScript 提取价格: ${price}")
                                break
                except Exception as e:
                    logger.debug(f"[Jarvis] JavaScript 提取失败: {e}")

            # 策略 3: 从 HTML 价格标签中提取
            if price == 0.0:
                try:
                    price_elem = soup.select_one('.price, .product-price, [data-price], .price-value, .starting-at-price')
                    if price_elem:
                        price_text = price_elem.get('data-price') or price_elem.text
                        price_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
                        if price_match:
                            price = float(price_match.group(1).replace(',', ''))
                            price_source = "html-element"
                            logger.info(f"[Jarvis] 从 HTML 元素提取价格: ${price}")
                except Exception as e:
                    logger.debug(f"[Jarvis] HTML 元素提取失败: {e}")

            # 策略 4: 降级方案 - 智能选择
            if price == 0.0:
                try:
                    price_matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', html)
                    prices = list(set([float(p.replace(',', '')) for p in price_matches if p]))
                    prices.sort()

                    # 过滤站立桌合理价格范围（$400-$3000）
                    reasonable_prices = [p for p in prices if 400 <= p <= 3000]

                    if reasonable_prices:
                        # 选择中位数价格
                        price = reasonable_prices[len(reasonable_prices) // 2]
                        price_source = "fallback-median"
                        logger.warning(f"[Jarvis] 使用降级方案（中位数）: ${price}")
                    else:
                        # 最后的降级：选择最高价格
                        high_prices = [p for p in prices if p >= 200]
                        if high_prices:
                            price = max(high_prices)
                            price_source = "fallback-max"
                            logger.warning(f"[Jarvis] 使用降级方案（最高价）: ${price}")
                except Exception as e:
                    logger.error(f"[Jarvis] 降级方案失败: {e}")

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
                    if "jarvis" in alt.lower() or "desk" in alt.lower():
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
                "brand": "Jarvis",
                "url": url,
                "title": title,
                "price": price,
                "currency": "USD",
                "description": description[:500],
                "image_url": image_url,
                "rating": None,
                "review_count": 0,
                "in_stock": True,
                "price_extraction_method": price_source,  # 价格提取方法
            }

            logger.info(f"[Jarvis] 产品信息提取成功: {title}")
            return result

        except Exception as e:
            logger.error(f"[Jarvis] 提取失败: {e}")
            return {"brand": "Jarvis", "url": url, "error": str(e)}
    
    async def get_product_specs(self, url: str) -> Dict[str, Any]:
        """获取产品详细规格"""
        logger.info(f"[Jarvis] 获取产品规格: {url}")

        try:
            # 获取产品页面
            html = await self._fetch_html(url, use_js=True)
            soup = self._parse_html(html)

            specs = {}

            # 查找规格表（常见的选择器）
            spec_selectors = [
                ".specs-table",
                ".specifications",
                ".product-specs",
                "table.specs",
                "[class*='spec']",
            ]

            spec_table = None
            for selector in spec_selectors:
                spec_table = soup.select_one(selector)
                if spec_table:
                    break

            if spec_table:
                # 从表格中提取规格
                rows = spec_table.select("tr")
                for row in rows:
                    cols = row.select("td, th")
                    if len(cols) >= 2:
                        key = self._clean_text(cols[0].text)
                        value = self._clean_text(cols[1].text)
                        if key and value:
                            specs[key] = value

            # 如果没有找到表格，尝试从列表中提取
            if not specs:
                spec_lists = soup.select("ul.specs li, .specifications li")
                for item in spec_lists:
                    text = self._clean_text(item.text)
                    if ":" in text:
                        parts = text.split(":", 1)
                        if len(parts) == 2:
                            specs[parts[0].strip()] = parts[1].strip()

            # 提取常见规格字段
            common_specs = {
                "dimensions": None,
                "weight_capacity": None,
                "height_range": None,
                "material": None,
                "warranty": None,
            }

            for key, value in specs.items():
                key_lower = key.lower()
                if "dimension" in key_lower or "size" in key_lower:
                    common_specs["dimensions"] = value
                elif "weight" in key_lower and "capacity" in key_lower:
                    common_specs["weight_capacity"] = value
                elif "height" in key_lower and "range" in key_lower:
                    common_specs["height_range"] = value
                elif "material" in key_lower:
                    common_specs["material"] = value
                elif "warranty" in key_lower:
                    common_specs["warranty"] = value

            result = {
                "brand": "Jarvis",
                "url": url,
                "specs": specs,
                "common_specs": common_specs,
            }

            logger.info(f"[Jarvis] 规格提取成功，共 {len(specs)} 项")
            return result

        except Exception as e:
            logger.error(f"[Jarvis] 规格提取失败: {e}")
            return {"brand": "Jarvis", "url": url, "specs": {}, "error": str(e)}

    async def search_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索产品"""
        logger.info(f"[Jarvis] 搜索产品: {keyword}, limit={limit}")

        try:
            # Fully/Jarvis 搜索 URL
            search_url = f"{self.BASE_URL}/search?q={keyword.replace(' ', '+')}"

            # 获取搜索结果页面
            html = await self._fetch_html(search_url, use_js=True)
            soup = self._parse_html(html)

            products = []

            # 查找产品列表
            product_selectors = [
                ".product-item",
                ".product-card",
                ".search-result",
                "article.product",
                ".product",
            ]

            product_elements = []
            for selector in product_selectors:
                product_elements = soup.select(selector)
                if product_elements:
                    logger.debug(f"[Jarvis] 使用选择器: {selector}, 找到 {len(product_elements)} 个产品")
                    break

            if not product_elements:
                logger.warning(f"[Jarvis] 未找到产品列表，尝试从链接中提取")
                # 降级方案：查找所有产品链接
                all_links = soup.find_all("a", href=True)
                for link in all_links:
                    href = link.get("href", "")
                    if "/products/" in href or "/jarvis" in href.lower():
                        title = self._clean_text(link.text) or "Unknown Product"
                        if len(title) > 5 and "jarvis" in title.lower():
                            products.append({
                                "brand": "Jarvis",
                                "title": title,
                                "url": self._make_absolute_url(href, self.BASE_URL),
                                "price": None,
                                "image_url": None,
                            })
                            if len(products) >= limit:
                                break
            else:
                # 从产品元素中提取信息
                for elem in product_elements[:limit]:
                    try:
                        # 提取标题
                        title_elem = elem.select_one("h2, h3, h4, .product-title, .product-name")
                        title = self._clean_text(title_elem.text) if title_elem else "Unknown Product"

                        # 提取链接
                        link_elem = elem.select_one("a[href]")
                        url = self._make_absolute_url(link_elem.get("href"), self.BASE_URL) if link_elem else None

                        # 提取价格
                        price_elem = elem.select_one(".price, .product-price, [class*='price']")
                        price = self._parse_price(price_elem.text) if price_elem else None

                        # 提取图片
                        img_elem = elem.select_one("img")
                        image_url = None
                        if img_elem:
                            image_url = img_elem.get("src") or img_elem.get("data-src")
                            if image_url:
                                image_url = self._make_absolute_url(image_url, self.BASE_URL)

                        if title and url:
                            products.append({
                                "brand": "Jarvis",
                                "title": title,
                                "url": url,
                                "price": price,
                                "image_url": image_url,
                            })
                    except Exception as e:
                        logger.warning(f"[Jarvis] 提取产品信息失败: {e}")
                        continue

            logger.info(f"[Jarvis] 搜索完成，找到 {len(products)} 个产品")
            return products

        except Exception as e:
            logger.error(f"[Jarvis] 搜索失败: {e}")
            return []

