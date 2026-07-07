from __future__ import annotations

from pathlib import Path


def test_detail_view_blocks_unready_data_and_shows_checklist() -> None:
    """Detail page should render readiness status and final checklist helpers."""

    source = Path("app/ui/stock_analysis_view.py").read_text(encoding="utf-8")
    assert "is_decision_allowed" in source
    assert "render_data_quality_status" in source
    assert "render_final_trading_checklist" in source
    assert "AI 판단과 점수를 제공하지 않습니다" in source
