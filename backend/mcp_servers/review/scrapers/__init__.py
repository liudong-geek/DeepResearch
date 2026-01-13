"""
Review Scrapers

评论爬虫实现
"""
from .amazon import AmazonReviewScraper
from .reddit import RedditReviewScraper

__all__ = ["AmazonReviewScraper", "RedditReviewScraper"]

