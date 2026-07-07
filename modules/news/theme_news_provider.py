from __future__ import annotations

from modules.news.news_models import ThemeNewsResult
from modules.news.news_provider import get_demo_news
from modules.theme.theme_mapping import get_theme_assets


def get_theme_news(theme: str) -> ThemeNewsResult:
    """Fetch theme news with demo fallback.

    This Sprint intentionally avoids paid or mandatory news APIs.
    """

    assets = get_theme_assets(theme)
    tickers = [asset.ticker for asset in assets]
    return get_demo_news(theme, tickers, "실제 뉴스 API는 아직 연결하지 않았습니다.")
