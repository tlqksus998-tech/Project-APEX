from __future__ import annotations


def test_beginner_mode_ui_modules_importable():
    import app.ui.checklist_view as checklist_view
    import app.ui.indicator_visuals as indicator_visuals
    import app.ui.stock_analysis_view as stock_analysis_view

    assert callable(checklist_view.render_analysis_checklist)
    assert callable(indicator_visuals.render_rsi_gauge)
    assert callable(stock_analysis_view.render_stock_analysis_view)


def test_stock_analysis_view_accepts_beginner_mode_argument():
    import inspect
    from app.ui.stock_analysis_view import render_stock_analysis_view

    signature = inspect.signature(render_stock_analysis_view)
    assert "beginner_mode" in signature.parameters
    assert signature.parameters["beginner_mode"].default is True
