"""
爬虫基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import random

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import async_playwright, Browser, Page
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)


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
        """获取 Playwright 浏览器实例（增强反检测）"""
        if self._browser is None:
            self._playwright = await async_playwright().start()

            # 增强的浏览器启动参数（绕过反爬虫检测）
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                ]
            )
            logger.debug("Playwright 浏览器已启动（反检测模式）")
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, TimeoutError, Exception)),
        before_sleep=before_sleep_log(logger, logger.level("WARNING").no),
    )
    async def _fetch_html(self, url: str, use_js: bool = False) -> str:
        """
        获取网页 HTML（带重试机制）

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

        try:
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

        except httpx.HTTPStatusError as e:
            # 根据状态码决定是否重试
            if e.response.status_code == 404:
                logger.error(f"页面不存在 (404): {url}")
                raise  # 404 不重试
            elif e.response.status_code in (403, 429):
                logger.warning(f"访问受限 ({e.response.status_code}): {url}，将重试...")
                raise  # 403/429 重试
            elif e.response.status_code >= 500:
                logger.warning(f"服务器错误 ({e.response.status_code}): {url}，将重试...")
                raise  # 5xx 重试
            else:
                logger.error(f"HTTP 错误 ({e.response.status_code}): {url}")
                raise

        except Exception as e:
            logger.warning(f"抓取失败: {url}, 错误: {e}，将重试...")
            raise

    async def _fetch_html_with_js(self, url: str) -> str:
        """
        使用 Playwright 获取 JavaScript 渲染后的 HTML（增强反检测）

        Args:
            url: 网页 URL

        Returns:
            渲染后的 HTML 内容
        """
        browser = await self._get_browser()

        # 创建新的 Context（每次请求独立，避免状态污染）
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.headers['User-Agent'],
            locale='en-US',
            timezone_id='America/New_York',
            # 模拟真实浏览器的权限
            permissions=['geolocation'],
        )

        page = await context.new_page()

        try:
            # 注入脚本，隐藏 webdriver 特征
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // 覆盖 Chrome 对象
                window.chrome = {
                    runtime: {}
                };

                // 覆盖 permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)

            # 设置额外的 HTTP 头
            await page.set_extra_http_headers(self.headers)

            # 访问页面（使用更宽松的等待策略）
            try:
                # 先尝试等待网络空闲
                await page.goto(url, wait_until="networkidle", timeout=60000)
            except Exception as e:
                logger.warning(f"networkidle 超时，降级为 domcontentloaded: {e}")
                # 如果网络空闲超时，降级为 DOM 加载完成
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # 额外等待一下
                await page.wait_for_timeout(3000)

            # 模拟用户行为（随机滚动）
            scroll_distance = random.randint(300, 800)
            await page.evaluate(f"window.scrollTo(0, {scroll_distance})")
            await page.wait_for_timeout(random.randint(500, 1500))

            # 获取 HTML
            html = await page.content()

            # 检查是否被 Cloudflare 拦截
            if any(keyword in html for keyword in [
                "Checking your browser",
                "Just a moment",
                "Verify you are human",
                "cf-browser-verification",
                "challenge-platform"
            ]):
                logger.warning(f"检测到 Cloudflare/Bot 挑战: {url}")
                # 等待更长时间，让验证完成
                for i in range(3):
                    await page.wait_for_timeout(5000)
                    html = await page.content()

                    # 检查是否通过验证
                    if not any(keyword in html for keyword in [
                        "Checking your browser",
                        "Just a moment",
                        "Verify you are human"
                    ]):
                        logger.success(f"Cloudflare 挑战已通过 (尝试 {i+1}/3)")
                        break
                else:
                    logger.error(f"Cloudflare 挑战未通过，可能需要更高级的绕过方案")

            return html

        except Exception as e:
            logger.error(f"Playwright 抓取失败: {url}, 错误: {e}")
            raise
        finally:
            await page.close()
            await context.close()
    
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

