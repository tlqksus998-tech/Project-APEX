from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.data_quality import assess_market_data_freshness, build_trading_readiness


KST = ZoneInfo("Asia/Seoul")


def test_caution_data_is_reference_allowed() -> None:
    """Delayed but usable data should remain reference-allowed."""

    query = datetime(2026, 7, 8, 10, 0, tzinfo=KST)
    freshness = assess_market_data_freshness("005930", "KOSPI", query - timedelta(minutes=45), query)
    result = build_trading_readiness("005930", "삼성전자", "KOSPI", "pykrx", True, freshness, ai_score=70)

    assert result.readiness_level == "CAUTION"
    assert result.is_ready_for_reference is True
    assert result.warning_messages


def test_stale_data_is_blocked() -> None:
    """Stale data should not be reference-allowed."""

    query = datetime(2026, 7, 8, 10, 0, tzinfo=KST)
    freshness = assess_market_data_freshness("005930", "KOSPI", query - timedelta(minutes=90), query)
    result = build_trading_readiness("005930", "삼성전자", "KOSPI", "pykrx", True, freshness, ai_score=None)

    assert result.readiness_level == "BLOCKED"
    assert result.is_ready_for_reference is False
    assert result.price_label == "가격 기준 확인 불가"
