"""
爬虫基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import async_playwright, Browser, Page


class BaseScraper(ABC):
    """
    爬虫基类
    
    所有电商爬虫都应该继承此类
    """
    
    def __init__(self, rate_limiter: Any, cache: Any):
        """
        初始化爬虫

        Args:
            rate_limiter: 限速器
            cache: 缓存管理器
        """
        self.rate_limiter = rate_limiter
        self.cache = cache

        # HTTP 客户端配置
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        # Playwright 浏览器实例（延迟初始化）
        self._browser: Optional[Browser] = None
        self._playwright = None
    
    async def _get_browser(self) -> Browser:
        """获取 Playwright 浏览器实例"""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            logger.debug("Playwright 浏览器已启动")
        return self._browser

    async def _close_browser(self):
        """关闭 Playwright 浏览器"""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            logger.debug("Playwright 浏览器已关闭")

    async def _fetch_html(self, url: str, use_js: bool = False) -> str:
        """
        获取网页 HTML

        Args:
            url: 网页 URL
            use_js: 是否使用 JavaScript 渲染（Playwright）

        Returns:
            HTML 内容
        """
        # 检查缓存
        cache_key = f"html:{'js' if use_js else 'static'}:{url}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"HTML 缓存命中: {url}")
            return cached

        # 限速
        await self.rate_limiter.acquire()

        logger.info(f"正在抓取: {url} (JS={'是' if use_js else '否'})")

        if use_js:
            # 使用 Playwright 渲染 JavaScript
            html = await self._fetch_html_with_js(url)
        else:
            # 使用 httpx 获取静态 HTML
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()
                html = response.text

        # 存入缓存
        self.cache.set(cache_key, html)

        return html

    async def _fetch_html_with_js(self, url: str) -> str:
        """
        使用 Playwright 获取 JavaScript 渲染后的 HTML

        Args:
            url: 网页 URL

        Returns:
            渲染后的 HTML 内容
        """
        browser = await self._get_browser()
        page = await browser.new_page()

        try:
            # 设置 User-Agent
            await page.set_extra_http_headers(self.headers)

            # 访问页面（等待 DOM 加载完成即可，不等待所有网络请求）
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # 额外等待一下，确保 JavaScript 执行完成
            await page.wait_for_timeout(2000)

            # 获取 HTML
            html = await page.content()

            return html
        finally:
            await page.close()
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """
        解析 HTML
        
        Args:
            html: HTML 内容
            
        Returns:
            BeautifulSoup 对象
        """
        return BeautifulSoup(html, "html.parser")
    
    @abstractmethod
    async def get_product_info(self, url: str) -> Dict[str, Any]:
        """
        获取产品基本信息
        
        Args:
            url: 产品页面 URL
            
        Returns:
            产品信息字典
        """
        pass
    
    @abstractmethod
    async def get_product_specs(self, url: str) -> Dict[str, Any]:
        """
        获取产品详细规格
        
        Args:
            url: 产品页面 URL
            
        Returns:
            产品规格字典
        """
        pass
    
    @abstractmethod
    async def search_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索产品
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量
            
        Returns:
            产品列表
        """
        pass
    
    def _extract_price(self, text: str) -> Optional[float]:
        """
        从文本中提取价格
        
        Args:
            text: 文本
            
        Returns:
            价格（浮点数）
        """
        import re
        
        # 移除逗号和货币符号
        text = text.replace(",", "").replace("$", "").strip()
        
        # 提取数字
        match = re.search(r"(\d+\.?\d*)", text)
        if match:
            return float(match.group(1))
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本（移除多余空白）
        
        Args:
            text: 文本
            
        Returns:
            清理后的文本
        """
        import re
        
        # 移除多余空白
        text = re.sub(r"\s+", " ", text)
        return text.strip()

