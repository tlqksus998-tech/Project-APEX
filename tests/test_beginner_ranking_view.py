from __future__ import annotations

from pathlib import Path


def test_beginner_ranking_view_uses_unified_ranking_service() -> None:
    """Beginner ranking should call the shared AI ranking service, not sample scores."""

    source = Path("app/ui/beginner_ranking_view.py").read_text(encoding="utf-8")
    assert "build_ai_ranking" in source
    assert "NASDAQ_SAMPLE" not in source
    assert "screen_today_candidates" not in source
    assert "ai_rank_detail_" in source


def test_beginner_ranking_view_does_not_mutate_navigation_widget_keys() -> None:
    """Ranking buttons must not directly modify widget-owned route keys."""

    source = Path("app/ui/beginner_ranking_view.py").read_text(encoding="utf-8")
    assert 'st.session_state["apex_track"]' not in source
    assert 'st.session_state["easy_menu"]' not in source
    assert 'st.session_state["selected_analysis_ticker"]' in source
    assert 'st.session_state["selected_analysis_market"]' in source
