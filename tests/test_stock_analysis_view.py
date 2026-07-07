from __future__ import annotations


def test_stock_analysis_view_importable():
    import app.ui.stock_analysis_view as view

    assert callable(view.render_stock_analysis_view)
    assert callable(view.analyze_selected_stock)


def test_stock_analysis_can_use_search_result_without_portfolio():
    from app.ui.portfolio_view import build_search_results

    results = build_search_results("삼성전자")
    assert isinstance(results, list)
