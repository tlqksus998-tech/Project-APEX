from __future__ import annotations


def test_theme_radar_ui_importable():
    import app.ui.theme_news_view as news_view
    import app.ui.theme_radar_view as radar_view

    assert callable(radar_view.render_theme_radar)
    assert callable(news_view.render_theme_news)
