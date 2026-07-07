from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.data_quality import assess_market_data_freshness, is_decision_source_allowed


KST = ZoneInfo("Asia/Seoul")


def test_fresh_regular_market_data_allows_decision() -> None:
    """Fresh regular-session data should be allowed."""

    query = datetime(2026, 7, 8, 10, 0, tzinfo=KST)
    data_time = query - timedelta(minutes=15)
    freshness = assess_market_data_freshness("005930", "KOSPI", data_time, query)

    assert freshness.freshness_status == "fresh"
    assert freshness.is_stale is False
    assert freshness.is_trade_time is True


def test_stale_regular_market_data_blocks_decision() -> None:
    """Regular-session data older than 60 minutes should be stale."""

    query = datetime(2026, 7, 8, 10, 30, tzinfo=KST)
    data_time = query - timedelta(minutes=90)
    freshness = assess_market_data_freshness("005930", "KOSPI", data_time, query)

    assert freshness.freshness_status == "stale"
    assert freshness.is_stale is True


def test_unknown_timestamp_is_unknown_and_stale() -> None:
    """Missing data timestamp should be marked unknown."""

    query = datetime(2026, 7, 8, 10, 0, tzinfo=KST)
    freshness = assess_market_data_freshness("005930", "KOSPI", None, query)

    assert freshness.freshness_status == "unknown"
    assert freshness.is_stale is True


def test_fallback_sample_demo_sources_are_not_allowed() -> None:
    """Fallback-like sources must not be used for AI judgement."""

    for source in ["fallback", "sample", "demo", "mock", "dummy", "placeholder", "example"]:
        assert is_decision_source_allowed(source, success=True) is False
    assert is_decision_source_allowed("pykrx", success=True) is True
    assert is_decision_source_allowed("yfinance", success=True) is True
    assert is_decision_source_allowed("test", success=True) is True
    assert is_decision_source_allowed("pykrx", success=False) is False
