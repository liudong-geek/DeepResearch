"""
文章内容爬虫实现
"""
from typing import Any, Dict, List
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from loguru import logger

from .base import BaseContentScraper


class ArticleContentScraper(BaseContentScraper):
    """
    文章内容爬虫
    
    抓取测评文章内容（Wirecutter, RTINGS, PCMag 等）
    """
    
    # 支持的网站配置
    SITE_CONFIGS = {
        "wirecutter.com": {
            "title_selector": "h1.entry-title, h1[class*='title']",
            "content_selector": "div.entry-content, article[class*='content']",
            "author_selector": "span.author, a[rel='author']",
        },
        "rtings.com": {
            "title_selector": "h1.title, h1[class*='title']",
            "content_selector": "div.article-content, div[class*='content']",
            "author_selector": "span.author",
        },
        "pcmag.com": {
            "title_selector": "h1.title, h1[class*='title']",
            "content_selector": "div.article-body, div[class*='body']",
            "author_selector": "span.author-name",
        },
        # 通用配置（作为后备）
        "default": {
            "title_selector": "h1, title",
            "content_selector": "article, main, div[class*='content'], div[class*='article']",
            "author_selector": "span[class*='author'], a[class*='author']",
        }
    }
    
    async def get_content(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        搜索文章（简单实现：返回空列表）
        
        Args:
            query: 搜索关键词
            limit: 返回内容数量
            
        Returns:
            内容列表
        """
        logger.info(f"[Article] 搜索文章: {query}, limit={limit}")
        
        # 简单实现：返回空列表
        # 实际应该调用搜索引擎 API 或爬取搜索结果
        return {
            "source": "article",
            "query": query,
            "total": 0,
            "contents": [],
            "note": "Article search not implemented. Use extract_article() with direct URL.",
        }
    
    async def extract_article(
        self,
        url: str
    ) -> Dict[str, Any]:
        """
        提取文章内容
        
        Args:
            url: 文章 URL
            
        Returns:
            文章内容
        """
        logger.info(f"[Article] 提取文章: {url}")
        
        try:
            # 获取网站配置
            domain = urlparse(url).netloc.replace("www.", "")
            config = self.SITE_CONFIGS.get(domain, self.SITE_CONFIGS["default"])
            
            # 限速
            await self.rate_limiter.acquire()
            
            # 获取 HTML
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                html = response.text
            
            # 解析 HTML
            soup = BeautifulSoup(html, "html.parser")
            
            # 提取标题
            title = ""
            title_elem = soup.select_one(config["title_selector"])
            if title_elem:
                title = self._clean_text(title_elem.get_text())
            
            # 提取作者
            author = ""
            author_elem = soup.select_one(config["author_selector"])
            if author_elem:
                author = self._clean_text(author_elem.get_text())
            
            # 提取内容
            content = ""
            content_elem = soup.select_one(config["content_selector"])
            if content_elem:
                # 移除脚本和样式
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                # 提取段落
                paragraphs = []
                for p in content_elem.find_all(["p", "h2", "h3", "li"]):
                    text = self._clean_text(p.get_text())
                    if text and len(text) > 20:  # 过滤太短的段落
                        paragraphs.append(text)
                
                content = "\n\n".join(paragraphs)
            
            result = {
                "source": "article",
                "type": "article",
                "url": url,
                "domain": domain,
                "title": title,
                "author": author,
                "content": content,
                "content_length": len(content),
            }
            
            logger.info(f"[Article] 提取成功，内容长度: {len(content)} 字符")
            return result
            
        except Exception as e:
            logger.error(f"[Article] 提取文章失败: {e}")
            return {
                "source": "article",
                "type": "article",
                "url": url,
                "error": str(e),
            }

