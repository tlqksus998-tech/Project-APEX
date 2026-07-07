from __future__ import annotations

import streamlit as st

from app.ui.brand_header import render_brand_header
from app.ui.freshness_view import render_freshness_bar, render_freshness_sidebar
from app.ui.home_view import render_home_page
from app.ui.market_briefing_view import render_market_briefing_page
from app.ui.market_leaders_view import render_market_leaders
from app.ui.page_context import PageContext
from app.ui.portfolio_manage_view import render_portfolio_manage_page
from app.ui.pro_gate_view import render_disclaimer
from app.ui.settings_view import render_settings_page
from app.ui.stock_analysis_view import render_stock_analysis_view
from app.ui.theme_radar_view import render_theme_radar
from modules.market.market_leaders import get_market_leaders

PAGE_ROUTES = {
    "내 투자 현황": render_home_page,
    "종목 판단 보기": None,
    "시장 주도주": None,
    "테마 레이더": None,
    "포트폴리오 관리": render_portfolio_manage_page,
    "시장 브리핑": render_market_briefing_page,
    "설정": render_settings_page,
}


def render_page(context: PageContext) -> None:
    """Route selected menu to its page renderer."""

    renderer = resolve_renderer(context.selected_menu)
    renderer(context)


def resolve_renderer(menu_name: str):
    """Return renderer for a menu name."""

    if menu_name == "종목 판단 보기":
        return render_stock_analysis_page
    if menu_name == "시장 주도주":
        return render_market_leaders_page
    if menu_name == "테마 레이더":
        return render_theme_radar_page
    return PAGE_ROUTES.get(menu_name) or render_not_ready_page


def render_stock_analysis_page(context: PageContext) -> None:
    """Render stock analysis page."""

    render_brand_header(context.freshness)
    render_disclaimer(context.beginner_mode)
    render_freshness_bar(context.freshness)
    default_query = str(st.session_state.get("selected_analysis_ticker", ""))
    render_stock_analysis_view(default_query=default_query)
    render_freshness_sidebar(context.freshness)


def render_market_leaders_page(context: PageContext) -> None:
    """Render market leaders page."""

    render_brand_header(context.freshness)
    render_disclaimer(context.beginner_mode)
    render_freshness_bar(context.freshness)
    with st.spinner("시장 주도주 데이터를 준비하는 중입니다..."):
        leaders = get_market_leaders()
    render_market_leaders(leaders)
    render_freshness_sidebar(context.freshness)


def render_theme_radar_page(context: PageContext) -> None:
    """Render theme radar page."""

    render_brand_header(context.freshness)
    render_disclaimer(context.beginner_mode)
    render_freshness_bar(context.freshness)
    render_theme_radar()
    render_freshness_sidebar(context.freshness)


def render_not_ready_page(context: PageContext) -> None:
    """Render fallback page for unknown menus."""

    render_brand_header(context.freshness)
    render_freshness_bar(context.freshness)
    st.info("아직 준비 중인 메뉴입니다.")
