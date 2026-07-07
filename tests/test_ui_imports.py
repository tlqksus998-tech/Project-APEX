from __future__ import annotations


def test_page_modules_importable():
    import app.ui.home_view
    import app.ui.market_briefing_view
    import app.ui.page_context
    import app.ui.portfolio_manage_view
    import app.ui.router
    import app.ui.settings_view

    assert callable(app.ui.home_view.render_home_page)
    assert callable(app.ui.market_briefing_view.render_market_briefing_page)
    assert callable(app.ui.portfolio_manage_view.render_portfolio_manage_page)
    assert callable(app.ui.settings_view.render_settings_page)
