"""
电商爬虫模块
"""
from .base import BaseScraper
from .uplift import UpliftScraper
from .jarvis import JarvisScraper
from .vari import VariScraper

__all__ = [
    "BaseScraper",
    "UpliftScraper",
    "JarvisScraper",
    "VariScraper",
]

