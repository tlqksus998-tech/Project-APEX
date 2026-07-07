from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from modules.data_quality.market_clock import get_market_session


NY = ZoneInfo("America/New_York")


def test_us_market_sessions() -> None:
    """US sessions should follow New York market hours."""

    assert get_market_session("NASDAQ", datetime(2026, 7, 8, 8, 0, tzinfo=NY))[0] == "pre_market"
    assert get_market_session("NASDAQ", datetime(2026, 7, 8, 10, 0, tzinfo=NY))[0] == "regular"
    assert get_market_session("NASDAQ", datetime(2026, 7, 8, 17, 0, tzinfo=NY))[0] == "after_market"
    assert get_market_session("NASDAQ", datetime(2026, 7, 8, 22, 0, tzinfo=NY))[0] == "closed"
