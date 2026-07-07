"""News intelligence package."""

from modules.news.news_models import ThemeNewsItem, ThemeNewsResult
from modules.news.theme_news_provider import get_theme_news

__all__ = ["ThemeNewsItem", "ThemeNewsResult", "get_theme_news"]
