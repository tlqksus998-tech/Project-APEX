from __future__ import annotations

from pathlib import Path


def test_beginner_views_importable():
    import app.ui.beginner_ranking_view as ranking_view
    import app.ui.beginner_stock_view as stock_view
    import app.ui.visual_components as visual_components

    assert callable(stock_view.render_beginner_stock_analysis)
    assert callable(ranking_view.render_beginner_ai_ranking)
    assert callable(visual_components.render_score_bar)


def test_beginner_ranking_does_not_mutate_widget_keys():
    source = Path("app/ui/beginner_ranking_view.py").read_text(encoding="utf-8")

    assert 'st.session_state["apex_track"]' not in source
    assert "st.session_state.apex_track" not in source
    assert 'st.session_state["easy_menu"]' not in source
    assert 'st.session_state["selected_analysis_ticker"]' in source
