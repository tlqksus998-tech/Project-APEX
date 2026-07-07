from __future__ import annotations

from modules.data_quality.trading_readiness import build_price_label


def test_us_extended_hours_price_labels() -> None:
    """US price labels should identify extended-hours context."""

    assert "프리장" in build_price_label("NASDAQ", "pre_market", "CAUTION")
    assert "애프터장" in build_price_label("NASDAQ", "after_market", "CAUTION")
