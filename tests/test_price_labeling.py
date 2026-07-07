from __future__ import annotations

from modules.data_quality.trading_readiness import build_price_label


def test_price_labels_match_market_session() -> None:
    """Price labels should avoid realtime claims."""

    assert build_price_label("KOSPI", "regular", "READY") == "최근 조회 가격"
    assert build_price_label("KOSPI", "closed", "CAUTION") == "최근 거래일 기준 가격"
    assert build_price_label("NASDAQ", "pre_market", "CAUTION") == "프리장 기준 최근 가격"
    assert build_price_label("NASDAQ", "after_market", "CAUTION") == "애프터장 기준 최근 가격"
    assert build_price_label("NASDAQ", "regular", "READY") == "최근 조회 가격"
    assert build_price_label("NASDAQ", "regular", "BLOCKED") == "가격 기준 확인 불가"
