from __future__ import annotations

from modules.data_quality.trading_readiness import build_final_trading_checklist


def test_korean_checklist_has_base_items_only() -> None:
    """Korean checklist should not include US extended-hours items."""

    checklist = build_final_trading_checklist("KOSPI")
    assert len(checklist) == 6
    assert not any("프리장" in item for item in checklist)


def test_us_checklist_has_extended_hours_items() -> None:
    """US checklist should include extended-hours confirmation."""

    checklist = build_final_trading_checklist("NASDAQ")
    assert len(checklist) >= 9
    assert any("프리장" in item for item in checklist)
