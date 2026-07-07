from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.data_quality import assess_market_data_freshness, build_trading_readiness


KST = ZoneInfo("Asia/Seoul")


def test_ready_real_data_builds_ready_readiness() -> None:
    """Fresh real data should be ready for reference."""

    query = datetime(2026, 7, 8, 10, 0, tzinfo=KST)
    freshness = assess_market_data_freshness("005930", "KOSPI", query - timedelta(minutes=10), query)
    result = build_trading_readiness("005930", "삼성전자", "KOSPI", "pykrx", True, freshness, ai_score=80)

    assert result.readiness_level == "READY"
    assert result.is_ready_for_reference is True
    assert result.sample_data_status == "clean"
    assert result.price_label == "최근 조회 가격"


def test_fallback_data_builds_blocked_readiness() -> None:
    """Fallback data should be blocked for AI judgement."""

    query = datetime(2026, 7, 8, 10, 0, tzinfo=KST)
    freshness = assess_market_data_freshness("005930", "KOSPI", query - timedelta(minutes=10), query)
    result = build_trading_readiness("005930", "삼성전자", "KOSPI", "fallback", False, freshness)

    assert result.readiness_level == "BLOCKED"
    assert result.is_ready_for_reference is False
    assert result.sample_data_status == "blocked"
    assert result.blocking_reasons


def test_final_trading_checklist_contains_required_items() -> None:
    """Checklist should include educational final checks."""

    query = datetime(2026, 7, 8, 10, 0, tzinfo=KST)
    freshness = assess_market_data_freshness("AAPL", "NASDAQ", query - timedelta(minutes=10), query)
    result = build_trading_readiness("AAPL", "Apple", "NASDAQ", "yfinance", True, freshness, ai_score=75)

    assert len(result.checklist) >= 9
    assert any("자동매매" in item for item in result.checklist)
    assert any("프리장" in item or "애프터장" in item for item in result.checklist)
