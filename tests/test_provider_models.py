from __future__ import annotations

from datetime import datetime

from modules.data_providers.provider_models import FxRateResult, LivePriceResult, MarketIndexResult
from modules.market.market_leaders import MarketLeaderItem
from modules.news.news_models import ThemeNewsItem
from modules.theme.theme_models import ThemeStrengthResult


def test_provider_models_create_successfully():
    now = datetime.now()
    assert LivePriceResult("A", "A", "US", 1, 0, 0, 0, 0, 0, "USD", now, "test", True, False).success is True
    assert FxRateResult("USD/KRW", 1380, now, "test", True, False).rate == 1380
    assert MarketIndexResult("^GSPC", "S&P500", 1, 0, 0, now, "test", True, False).symbol == "^GSPC"
    assert MarketLeaderItem(1, "A", "A", "US", 1, 0, 0, 0, "USD", "now", "test").rank == 1
    assert ThemeStrengthResult("AI", 0, 0, 0, 0, "중립", [], now, "test", True, False).theme == "AI"
    assert ThemeNewsItem("title", "source", now, "", "summary", "AI", [], "Low", "중립", True).is_fallback is True
