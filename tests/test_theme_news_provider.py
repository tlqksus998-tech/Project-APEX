from __future__ import annotations

from modules.news.theme_news_provider import get_theme_news


def test_theme_news_provider_returns_demo_result():
    result = get_theme_news("반도체")
    assert result.items
    assert result.is_fallback is True
    assert result.items[0].published_at is not None
    assert result.items[0].source
