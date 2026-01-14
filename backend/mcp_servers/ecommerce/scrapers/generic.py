"""
通用电商爬虫实现

用于抓取大多数电商网站的产品信息
"""
from typing import Any, Dict, List
import re

from loguru import logger

from .base import BaseScraper


class GenericScraper(BaseScraper):
    """
    通用电商爬虫
    
    使用启发式方法提取产品信息，适用于大多数电商网站
    """
    
    def __init__(self, brand_name: str, rate_limiter, cache):
        """
        初始化通用爬虫
        
        Args:
            brand_name: 品牌名称（用于日志和结果标识）
            rate_limiter: 限速器
            cache: 缓存管理器
        """
        super().__init__(rate_limiter, cache)
        self.brand_name = brand_name
    
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        """
        获取产品基本信息
        
        使用启发式方法提取：
        1. 标题：第一个 h1 标签
        2. 价格：正则匹配 $xxx.xx 格式
        3. 描述：第一个长段落
        4. 图片：第一个产品相关图片
        """
        logger.info(f"[{self.brand_name}] 获取产品信息: {url}")
        
        try:
            # 使用 JavaScript 渲染（大多数现代电商网站需要）
            html = await self._fetch_html(url, use_js=True)
            soup = self._parse_html(html)
            
            # 1. 提取标题
            title = self._extract_title(soup)

            # 2. 提取价格（返回价格和元数据）
            price, price_metadata = self._extract_price_from_html(html)

            # 3. 提取描述
            description = self._extract_description(soup)

            # 4. 提取图片
            image_url = self._extract_image(soup, url)

            # 价格验证和警告
            price_warning = price_metadata.get("warning", None)
            if price == 0.0:
                additional_warning = "未找到价格信息，可能需要登录或联系销售"
                price_warning = f"{price_warning}; {additional_warning}" if price_warning else additional_warning
                logger.warning(f"[{self.brand_name}] {additional_warning}")
            elif price < 100:
                additional_warning = "价格异常偏低，可能是配件或数据抓取错误"
                price_warning = f"{price_warning}; {additional_warning}" if price_warning else additional_warning
                logger.warning(f"[{self.brand_name}] {additional_warning}: ${price}")
            elif price > 3000:
                additional_warning = "价格异常偏高，可能包含配件或套装"
                price_warning = f"{price_warning}; {additional_warning}" if price_warning else additional_warning
                logger.warning(f"[{self.brand_name}] {additional_warning}: ${price}")

            result = {
                "brand": self.brand_name,
                "url": url,
                "title": title,
                "price": price,
                "currency": "USD",
                "description": description[:500] if description else "",
                "image_url": image_url,
                "rating": None,
                "review_count": 0,
                "in_stock": True,
                "price_warning": price_warning,  # 添加价格警告
                "price_confidence": price_metadata.get("confidence", "unknown"),  # 添加置信度
                "price_extraction_method": price_metadata.get("method", "unknown"),  # 添加提取方法
            }

            logger.info(f"[{self.brand_name}] 产品信息提取成功: {title} - ${price}")
            return result
            
        except Exception as e:
            logger.error(f"[{self.brand_name}] 提取产品信息失败: {e}")
            return {
                "brand": self.brand_name,
                "url": url,
                "error": str(e),
            }
    
    def _extract_title(self, soup) -> str:
        """提取产品标题"""
        # 尝试多种选择器（按优先级排序）
        selectors = [
            "h1.product-title",
            "h1.product-name",
            "h1[itemprop='name']",
            ".product-title h1",
            ".product-name h1",
            "h1",  # 最后尝试任意 h1
            "title",  # 最后的备选方案
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                title = self._clean_text(elem.text)
                # 过滤掉太短或包含网站名的标题
                if title and len(title) > 5 and len(title) < 200:
                    # 移除常见的网站后缀
                    for suffix in [' | ', ' - ', ' – ']:
                        if suffix in title:
                            title = title.split(suffix)[0]
                    return title

        return "Unknown Product"
    
    def _extract_price_from_html(self, html: str) -> tuple[float, dict]:
        """
        从 HTML 中提取价格

        策略：
        1. 提取所有价格
        2. 过滤合理范围（$50-$5000）
        3. 优先选择主产品价格（$200-$2000）
        4. 如果没有主产品价格，选择次优价格

        Returns:
            tuple: (price, metadata) 其中 metadata 包含置信度和提取方法
        """
        # 匹配 $xxx.xx 或 $xxx,xxx.xx 格式
        price_matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', html)

        if not price_matches:
            logger.warning(f"[{self.brand_name}] 未找到价格信息")
            return 0.0, {
                "confidence": "none",
                "method": "no_price_found",
                "warning": "未找到价格信息，需人工验证"
            }

        # 转换为浮点数并去重
        prices = list(set([float(p.replace(',', '')) for p in price_matches]))
        prices.sort()  # 从小到大排序

        logger.debug(f"[{self.brand_name}] 找到价格: {prices[:10]}")  # 只显示前10个

        # 过滤合理价格范围（升降桌及配件通常 $50-$5000）
        reasonable_prices = [p for p in prices if 50 <= p <= 5000]

        if not reasonable_prices:
            logger.warning(f"[{self.brand_name}] 没有合理范围内的价格，使用原始价格")
            price = min(prices) if prices else 0.0
            return price, {
                "confidence": "low",
                "method": "fallback_min_price",
                "warning": "价格可能不准确，建议人工验证",
                "all_prices_found": len(prices)
            }

        # 优先选择主产品价格范围（$200-$2000）
        main_product_prices = [p for p in reasonable_prices if 200 <= p <= 2000]

        if main_product_prices:
            # 返回主产品价格中的最小值（通常是起始价）
            selected_price = min(main_product_prices)
            logger.info(f"[{self.brand_name}] 选择主产品价格: ${selected_price}")
            return selected_price, {
                "confidence": "medium",
                "method": "heuristic_main_product",
                "warning": "使用启发式算法提取，建议验证",
                "all_prices_found": len(prices),
                "candidates": len(main_product_prices)
            }

        # 如果没有主产品价格，选择次优价格（$100-$200 或 $2000-$5000）
        secondary_prices = [p for p in reasonable_prices if 100 <= p < 200 or 2000 < p <= 5000]

        if secondary_prices:
            # 优先选择较高的价格（更可能是主产品）
            selected_price = max(secondary_prices) if max(secondary_prices) > 200 else min(secondary_prices)
            logger.warning(f"[{self.brand_name}] 未找到主产品价格，选择次优价格: ${selected_price}")
            return selected_price, {
                "confidence": "low",
                "method": "heuristic_secondary",
                "warning": "未找到主产品价格，使用次优价格，需人工验证",
                "all_prices_found": len(prices),
                "candidates": len(secondary_prices)
            }

        # 最后的降级方案：选择最小的合理价格
        selected_price = min(reasonable_prices)
        logger.warning(f"[{self.brand_name}] 使用降级方案，选择最小价格: ${selected_price}")
        return selected_price, {
            "confidence": "low",
            "method": "fallback_min_reasonable",
            "warning": "使用降级方案，价格可能不准确，强烈建议人工验证",
            "all_prices_found": len(prices)
        }
    
    def _extract_description(self, soup) -> str:
        """提取产品描述"""
        # 尝试多种选择器（按优先级排序）
        selectors = [
            ".product-description",
            ".product-desc",
            ".description",
            "[itemprop='description']",
            ".product-details",
            ".product-info",
            "#product-description",
            "#description",
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                desc = self._clean_text(elem.text)
                if desc and len(desc) > 50:
                    return desc

        # 回退：查找第一个长段落（跳过导航和页脚）
        for p in soup.find_all("p"):
            # 跳过导航、页脚、Cookie 提示等
            parent_class = ' '.join(p.parent.get('class', []))
            if any(skip in parent_class.lower() for skip in ['nav', 'footer', 'cookie', 'header']):
                continue

            text = self._clean_text(p.text)
            if len(text) > 50 and len(text) < 1000:
                return text

        return ""
    
    def _extract_image(self, soup, base_url: str) -> str:
        """提取产品图片"""
        # 尝试多种选择器（按优先级排序）
        selectors = [
            ".product-image img",
            ".product-photo img",
            "[itemprop='image']",
            ".gallery img",
            ".product-gallery img",
            "#product-image img",
            ".main-image img",
        ]

        for selector in selectors:
            img = soup.select_one(selector)
            if img:
                src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
                if src and self._is_valid_image_url(src):
                    return self._make_absolute_url(src, base_url)

        # 回退：查找第一个有效的产品图片
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            alt = img.get("alt", "").lower()

            # 检查是否是产品图片
            if src and self._is_valid_image_url(src):
                # 优先选择 alt 包含 product/desk 的图片
                if any(keyword in alt for keyword in ['product', 'desk', 'table']):
                    return self._make_absolute_url(src, base_url)

        # 最后的回退：任意有效图片
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and self._is_valid_image_url(src):
                return self._make_absolute_url(src, base_url)

        return None

    def _is_valid_image_url(self, url: str) -> bool:
        """检查是否是有效的产品图片 URL"""
        if not url:
            return False

        url_lower = url.lower()

        # 排除常见的非产品图片
        exclude_keywords = [
            'logo', 'icon', 'sprite', 'banner', 'badge',
            'avatar', 'placeholder', 'loading', 'spinner',
            'facebook', 'twitter', 'instagram', 'social',
        ]

        for keyword in exclude_keywords:
            if keyword in url_lower:
                return False

        # 必须是图片格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        if not any(ext in url_lower for ext in image_extensions):
            # 如果没有明确的扩展名，检查是否包含图片相关的路径
            if not any(keyword in url_lower for keyword in ['image', 'img', 'photo', 'picture']):
                return False

        return True
    
    def _make_absolute_url(self, url: str, base_url: str) -> str:
        """将相对 URL 转换为绝对 URL"""
        if url.startswith("http"):
            return url
        elif url.startswith("//"):
            return "https:" + url
        elif url.startswith("/"):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{url}"
        else:
            return url
    
    async def get_product_specs(self, url: str) -> Dict[str, Any]:
        """获取产品详细规格"""
        logger.info(f"[{self.brand_name}] 获取产品规格: {url}")

        try:
            # 获取产品页面
            html = await self._fetch_html(url, use_js=True)
            soup = self._parse_html(html)

            specs = {}

            # 尝试多种常见的规格表选择器
            spec_selectors = [
                ".specs-table",
                ".specifications",
                ".product-specs",
                ".product-details",
                "table.specs",
                "[class*='spec']",
                "[id*='spec']",
            ]

            spec_container = None
            for selector in spec_selectors:
                spec_container = soup.select_one(selector)
                if spec_container:
                    logger.debug(f"[{self.brand_name}] 找到规格容器: {selector}")
                    break

            if spec_container:
                # 从表格中提取规格
                rows = spec_container.select("tr")
                for row in rows:
                    cols = row.select("td, th")
                    if len(cols) >= 2:
                        key = self._clean_text(cols[0].text)
                        value = self._clean_text(cols[1].text)
                        if key and value:
                            specs[key] = value

                # 如果表格没有数据，尝试从列表中提取
                if not specs:
                    items = spec_container.select("li, div")
                    for item in items:
                        text = self._clean_text(item.text)
                        if ":" in text:
                            parts = text.split(":", 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                if key and value:
                                    specs[key] = value

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
                elif "weight" in key_lower and ("capacity" in key_lower or "limit" in key_lower):
                    common_specs["weight_capacity"] = value
                elif "height" in key_lower and "range" in key_lower:
                    common_specs["height_range"] = value
                elif "material" in key_lower:
                    common_specs["material"] = value
                elif "warranty" in key_lower:
                    common_specs["warranty"] = value

            result = {
                "brand": self.brand_name,
                "url": url,
                "specs": specs,
                "common_specs": common_specs,
            }

            if specs:
                logger.info(f"[{self.brand_name}] 规格提取成功，共 {len(specs)} 项")
            else:
                logger.warning(f"[{self.brand_name}] 未找到规格信息")

            return result

        except Exception as e:
            logger.error(f"[{self.brand_name}] 规格提取失败: {e}")
            return {"brand": self.brand_name, "url": url, "specs": {}, "error": str(e)}
    
    async def search_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索产品（通用实现）"""
        logger.info(f"[{self.brand_name}] 搜索产品: {keyword}, limit={limit}")

        try:
            # 构建搜索 URL（尝试常见的搜索路径）
            search_paths = [
                f"/search?q={keyword.replace(' ', '+')}",
                f"/search/?q={keyword.replace(' ', '+')}",
                f"/search/{keyword.replace(' ', '-')}",
                f"/products?search={keyword.replace(' ', '+')}",
            ]

            products = []

            # 尝试每个搜索路径
            for search_path in search_paths:
                if products:  # 如果已经找到产品，跳出循环
                    break

                try:
                    # 构建完整的搜索 URL
                    # 需要从品牌名推断基础 URL
                    base_urls = {
                        "FlexiSpot": "https://www.flexispot.com",
                        "Autonomous": "https://www.autonomous.ai",
                        "Humanscale": "https://www.humanscale.com",
                        "IKEA": "https://www.ikea.com",
                    }

                    base_url = base_urls.get(self.brand_name, f"https://www.{self.brand_name.lower()}.com")
                    search_url = base_url + search_path

                    logger.debug(f"[{self.brand_name}] 尝试搜索 URL: {search_url}")

                    # 获取搜索结果页面
                    html = await self._fetch_html(search_url, use_js=True)
                    soup = self._parse_html(html)

                    # 查找产品列表
                    product_selectors = [
                        ".product-item",
                        ".product-card",
                        ".search-result",
                        "article.product",
                        ".product",
                        "[class*='product-']",
                    ]

                    product_elements = []
                    for selector in product_selectors:
                        product_elements = soup.select(selector)
                        if product_elements:
                            logger.debug(f"[{self.brand_name}] 使用选择器: {selector}, 找到 {len(product_elements)} 个产品")
                            break

                    if product_elements:
                        # 从产品元素中提取信息
                        for elem in product_elements[:limit]:
                            try:
                                # 提取标题
                                title_elem = elem.select_one("h2, h3, h4, .product-title, .product-name, [class*='title']")
                                title = self._clean_text(title_elem.text) if title_elem else None

                                # 提取链接
                                link_elem = elem.select_one("a[href]")
                                url = None
                                if link_elem:
                                    href = link_elem.get("href")
                                    url = self._make_absolute_url(href, base_url)

                                # 提取价格
                                price_elem = elem.select_one(".price, .product-price, [class*='price']")
                                price = self._parse_price(price_elem.text) if price_elem else None

                                # 提取图片
                                img_elem = elem.select_one("img")
                                image_url = None
                                if img_elem:
                                    image_url = img_elem.get("src") or img_elem.get("data-src")
                                    if image_url:
                                        image_url = self._make_absolute_url(image_url, base_url)

                                if title and url:
                                    products.append({
                                        "brand": self.brand_name,
                                        "title": title,
                                        "url": url,
                                        "price": price,
                                        "image_url": image_url,
                                    })
                            except Exception as e:
                                logger.warning(f"[{self.brand_name}] 提取产品信息失败: {e}")
                                continue

                except Exception as e:
                    logger.debug(f"[{self.brand_name}] 搜索路径 {search_path} 失败: {e}")
                    continue

            if not products:
                logger.warning(f"[{self.brand_name}] 未找到产品，搜索功能可能需要针对该品牌定制")
            else:
                logger.info(f"[{self.brand_name}] 搜索完成，找到 {len(products)} 个产品")

            return products

        except Exception as e:
            logger.error(f"[{self.brand_name}] 搜索失败: {e}")
            return []

