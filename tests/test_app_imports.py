def test_ui_modules_importable():
    import app.ui.analysis_view
    import app.ui.brand_header
    import app.ui.chart_view
    import app.ui.macro_view
    import app.ui.news_view
    import app.ui.market_leaders_view
    import app.ui.candidate_view
    import app.ui.decision_view
    import app.ui.design_system
    import app.ui.kpi_view
    import app.ui.layout
    import app.ui.market_view
    import app.ui.portfolio_view
    import app.ui.pro_gate_view
    import app.ui.risk_view
    import app.ui.router
    import app.ui.sidebar
    import app.ui.stock_analysis_view
    import app.ui.theme_news_view
    import app.ui.theme_radar_view
    import app.ui.today_dashboard

    assert "쉽게 보기 · 종목분석" in app.ui.sidebar.MENU_ITEMS
    assert "쉽게 보기 · AI 랭킹" in app.ui.sidebar.MENU_ITEMS
    assert "개발자 모드 · 내 투자 현황" in app.ui.sidebar.MENU_ITEMS
    assert "개발자 모드 · 포트폴리오 관리" in app.ui.sidebar.MENU_ITEMS
    assert callable(app.ui.portfolio_view.build_search_results)
    assert callable(app.ui.news_view.render_market_issues_placeholder)
    assert callable(app.ui.market_leaders_view.render_market_leaders)
    assert callable(app.ui.stock_analysis_view.render_stock_analysis_view)
    assert callable(app.ui.theme_radar_view.render_theme_radar)
    assert callable(app.ui.router.render_page)
    assert callable(app.ui.pro_gate_view.render_disclaimer)
    assert callable(app.ui.design_system.load_theme)
    assert callable(app.ui.kpi_view.render_kpi_summary)


def test_main_importable():
    import app.main

    assert callable(app.main.main)


def test_portfolio_session_module_importable():
    import modules.portfolio.session_state as session_state

    assert session_state.PORTFOLIO_STATE_KEY == "portfolio_df"



