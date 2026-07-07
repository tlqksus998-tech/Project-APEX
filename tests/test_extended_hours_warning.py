from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.data_quality import assess_market_data_freshness, build_trading_readiness


NY = ZoneInfo("America/New_York")


def test_pre_market_fresh_data_is_caution_with_warning() -> None:
    """Fresh pre-market US data should be caution with warning."""

    query = datetime(2026, 7, 8, 8, 0, tzinfo=NY)
    freshness = assess_market_data_freshness("AAPL", "NASDAQ", query - timedelta(minutes=5), query)
    result = build_trading_readiness("AAPL", "Apple", "NASDAQ", "yfinance", True, freshness, ai_score=80)

    assert result.readiness_level == "CAUTION"
    assert result.is_extended_hours is True
    assert result.extended_hours_type == "pre_market"
    assert "프리장" in result.extended_hours_warning


def test_after_market_fresh_data_is_caution_with_warning() -> None:
    """Fresh after-market US data should be caution with warning."""

    query = datetime(2026, 7, 8, 17, 0, tzinfo=NY)
    freshness = assess_market_data_freshness("AAPL", "NASDAQ", query - timedelta(minutes=5), query)
    result = build_trading_readiness("AAPL", "Apple", "NASDAQ", "yfinance", True, freshness, ai_score=80)

    assert result.readiness_level == "CAUTION"
    assert result.is_extended_hours is True
    assert result.extended_hours_type == "after_market"
    assert "애프터장" in result.extended_hours_warning
