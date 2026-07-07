from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.data_quality import assess_market_data_freshness


NY = ZoneInfo("America/New_York")


def test_us_regular_session_same_date_daily_data_is_caution_not_blocked() -> None:
    """US daily data during regular market hours can be CAUTION, not BLOCKED."""

    query = datetime(2026, 7, 7, 13, 0, tzinfo=NY)
    data_timestamp = datetime(2026, 7, 7, 0, 0, tzinfo=NY)
    freshness = assess_market_data_freshness("AAPL", "NASDAQ", data_timestamp, query)

    assert freshness.freshness_status == "delayed"
    assert freshness.readiness_level == "CAUTION"
    assert freshness.is_stale is False


def test_us_closed_market_recent_trade_data_is_caution_not_blocked() -> None:
    """Recent US data after market close should stay usable with caution."""

    query = datetime(2026, 7, 7, 18, 0, tzinfo=NY)
    data_timestamp = query - timedelta(hours=3)
    freshness = assess_market_data_freshness("AAPL", "NASDAQ", data_timestamp, query)

    assert freshness.freshness_status == "closed_market"
    assert freshness.readiness_level == "CAUTION"
    assert freshness.is_stale is False


def test_us_old_data_is_blocked() -> None:
    """Old US market data should still be blocked."""

    query = datetime(2026, 7, 7, 13, 0, tzinfo=NY)
    data_timestamp = query - timedelta(days=10)
    freshness = assess_market_data_freshness("AAPL", "NASDAQ", data_timestamp, query)

    assert freshness.freshness_status == "stale"
    assert freshness.readiness_level == "BLOCKED"
    assert freshness.is_stale is True
