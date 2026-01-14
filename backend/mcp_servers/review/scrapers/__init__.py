"""
Review Scrapers

评论爬虫实现
"""
from .trustpilot import TrustpilotReviewScraper
# from .amazon import AmazonReviewScraper  # 已移除：需要登录
# from .reddit import RedditReviewScraper  # 已移除：API 不稳定

__all__ = ["TrustpilotReviewScraper"]

