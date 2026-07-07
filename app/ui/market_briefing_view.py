from __future__ import annotations

from app.ui.brand_header import render_brand_header
from app.ui.chart_view import render_macro_mini_charts
from app.ui.freshness_view import render_freshness_bar, render_freshness_sidebar
from app.ui.macro_view import render_fear_greed_placeholder, render_macro_market_cards, render_morning_brief
from app.ui.news_view import render_market_issues_placeholder
from app.ui.page_context import PageContext
from app.ui.pro_gate_view import render_disclaimer


def render_market_briefing_page(context: PageContext) -> None:
    """Render macro market briefing page."""

    render_brand_header(context.freshness)
    render_disclaimer(context.beginner_mode)
    render_freshness_bar(context.freshness)
    render_morning_brief(context.macro_brief)
    render_macro_market_cards(context.macro_brief.overview)
    render_macro_mini_charts(context.macro_brief.dashboard)
    render_fear_greed_placeholder(context.sentiment)
    render_market_issues_placeholder()
    render_freshness_sidebar(context.freshness)
