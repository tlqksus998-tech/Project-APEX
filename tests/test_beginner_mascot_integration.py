from __future__ import annotations

from pathlib import Path


def test_beginner_views_import_mascot_helpers() -> None:
    """Beginner pages should reference the mascot UI layer."""

    stock_source = Path("app/ui/beginner_stock_view.py").read_text(encoding="utf-8")
    ranking_source = Path("app/ui/beginner_ranking_view.py").read_text(encoding="utf-8")
    home_source = Path("app/ui/home_view.py").read_text(encoding="utf-8")

    assert "app.ui.mascot" in stock_source
    assert "render_mascot_message" in ranking_source
    assert "render_empty_portfolio_mascot" in home_source
    assert "render_home_mascot" in home_source
    assert "tofu_pouch" in ranking_source


def test_app_main_imports_with_mascot_patch() -> None:
    """Main app module should remain importable after mascot role changes."""

    import app.main  # noqa: F401


def test_beginner_ranking_does_not_mutate_track_widget_keys() -> None:
    """Ranking detail buttons should not modify Streamlit widget-owned navigation keys."""

    source = Path("app/ui/beginner_ranking_view.py").read_text(encoding="utf-8")
    assert 'st.session_state["apex_track"]' not in source
    assert "st.session_state.apex_track" not in source
    assert 'st.session_state["easy_menu"]' not in source
    assert "selected_analysis_ticker" in source
