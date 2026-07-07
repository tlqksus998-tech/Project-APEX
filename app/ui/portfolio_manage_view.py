from __future__ import annotations

import streamlit as st

from app.ui.brand_header import render_brand_header
from app.ui.freshness_view import render_freshness_bar, render_freshness_sidebar
from app.ui.page_context import PageContext
from app.ui.portfolio_view import render_portfolio_input
from app.ui.pro_gate_view import render_disclaimer
from app.ui.today_dashboard import render_portfolio_summary
from modules.dashboard import run_dashboard_engines
from modules.portfolio.input_data import get_sample_portfolio, validate_portfolio
from modules.portfolio.session_state import get_portfolio_state

K_LOADING = "시장 데이터와 리스크를 분석하는 중입니다..."


def render_portfolio_manage_page(context: PageContext) -> None:
    """Render portfolio input, editing, storage, and summary management."""

    render_brand_header(context.freshness)
    render_disclaimer(context.beginner_mode)
    render_freshness_bar(context.freshness)
    render_portfolio_input(get_sample_portfolio())

    portfolio, _ = validate_portfolio(get_portfolio_state())
    if not portfolio.empty:
        with st.spinner(K_LOADING):
            _, _, positions, _, metrics, _ = run_dashboard_engines(
                portfolio,
                context.cash,
                context.period,
                context.interval,
                market_regime=context.macro_brief.market_signal,
            )
        render_portfolio_summary(positions, metrics, context.cash.total_cash_krw)
    render_freshness_sidebar(context.freshness)
