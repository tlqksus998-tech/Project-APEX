def test_ui_modules_importable():
    import app.ui.analysis_view
    import app.ui.brand_header
    import app.ui.chart_view
    import app.ui.macro_view
    import app.ui.news_view
    import app.ui.candidate_view
    import app.ui.decision_view
    import app.ui.layout
    import app.ui.market_view
    import app.ui.portfolio_view
    import app.ui.risk_view
    import app.ui.sidebar
    import app.ui.today_dashboard

    assert app.ui.sidebar.MENU_ITEMS == ["Home", "Portfolio", "Market", "Analysis", "Decision", "Settings"]
    assert callable(app.ui.portfolio_view.build_search_results)
    assert callable(app.ui.news_view.render_market_issues_placeholder)


def test_main_importable():
    import app.main

    assert callable(app.main.main)


def test_portfolio_session_module_importable():
    import modules.portfolio.session_state as session_state

    assert session_state.PORTFOLIO_STATE_KEY == "portfolio_df"

