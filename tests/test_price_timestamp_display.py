from __future__ import annotations

from pathlib import Path


def test_detail_and_ranking_views_display_data_timestamps() -> None:
    """Views should show separate data and query timestamps."""

    ranking_source = Path("app/ui/beginner_ranking_view.py").read_text(encoding="utf-8")
    detail_source = Path("app/ui/stock_analysis_view.py").read_text(encoding="utf-8")

    assert "데이터 기준 시간" in ranking_source
    assert "최근 조회" in ranking_source
    assert "데이터 기준" in detail_source
    assert "최근 조회" in detail_source


def test_refresh_button_keys_are_not_duplicate_prone() -> None:
    """No direct navigation widget mutation should be used for data refresh routing."""

    ranking_source = Path("app/ui/beginner_ranking_view.py").read_text(encoding="utf-8")
    assert 'st.session_state["apex_track"]' not in ranking_source
    assert 'st.session_state["easy_menu"]' not in ranking_source
