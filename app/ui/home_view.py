from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.brand_header import render_brand_header
from app.ui.candidate_view import render_candidate_stocks
from app.ui.chart_view import render_macro_mini_charts
from app.ui.freshness_view import render_freshness_bar, render_freshness_sidebar
from app.ui.help_text import render_terms_help
from app.ui.macro_view import render_fear_greed_placeholder, render_macro_market_cards, render_morning_brief
from app.ui.news_view import render_market_issues_placeholder
from app.ui.onboarding import render_empty_state, render_onboarding
from app.ui.page_context import PageContext
from app.ui.portfolio_engine_view import render_investment_os_header
from app.ui.portfolio_view import render_portfolio_errors, render_portfolio_input
from app.ui.pro_gate_view import render_disclaimer
from app.ui.summary_view import render_portfolio_ai_summary
from app.ui.today_dashboard import (
    build_dashboard_table,
    build_today_actions,
    compute_dashboard_scores,
    render_action_card,
    render_dashboard_table,
    render_decision_explanation_panel,
    render_portfolio_summary,
    render_risk_alerts,
    render_score_cards,
)
from modules.dashboard import run_dashboard_engines
from modules.data_freshness import build_freshness_snapshot, mark_analysis_run
from modules.portfolio.input_data import get_sample_portfolio, validate_portfolio
from modules.portfolio.session_state import get_portfolio_state
from modules.portfolio_engine import run_portfolio_engine
from modules.screening import screen_today_candidates
from modules.summary import generate_portfolio_summary

K_INPUT_TITLE = "포트폴리오 입력/수정"
K_LOADING = "시장 데이터와 리스크를 분석하는 중입니다..."


def render_home_page(context: PageContext) -> None:
    """Render compact home dashboard: summary, actions, alerts, and holdings decision overview."""

    portfolio, errors = validate_portfolio(get_portfolio_state())
    if portfolio.empty:
        render_empty_home(context)
        return

    with st.spinner(K_LOADING):
        market_overview, analysis_results, positions, portfolio_risk, metrics, decision_results = run_dashboard_engines(
            portfolio,
            context.cash,
            context.period,
            context.interval,
            market_regime=context.macro_brief.market_signal,
        )
    analysis_run_at = mark_analysis_run()
    freshness = build_freshness_snapshot(
        fx_rate=context.cash.usdkrw,
        fx_updated_at=st.session_state.get("fx_updated_at"),
        fx_source=st.session_state.get("fx_source", "manual"),
        price_updated_at=analysis_run_at if not market_overview.empty else None,
        analysis_run_at=analysis_run_at,
        macro_updated_at=context.macro_brief.updated_at,
    )
    render_freshness_sidebar(freshness)

    scores = compute_dashboard_scores(decision_results, portfolio_risk)
    actions = build_today_actions(positions, portfolio_risk, scores)
    dashboard_table = build_dashboard_table(positions, analysis_results, decision_results, portfolio_risk)
    portfolio_snapshot = run_portfolio_engine(positions, metrics, context.cash)
    portfolio_summary = generate_portfolio_summary(metrics, positions, decision_results, portfolio_risk, context.cash.total_cash_krw)

    render_brand_header(freshness)
    render_disclaimer(context.beginner_mode)
    render_freshness_bar(freshness)
    render_portfolio_ai_summary(portfolio_summary)
    render_action_card(actions)
    render_investment_os_header(portfolio_snapshot)
    render_dashboard_table(dashboard_table, beginner_mode=context.beginner_mode)
    render_risk_alerts(portfolio_risk)
    render_quick_links()

    with st.expander("상세 판단 지표", expanded=not context.beginner_mode):
        render_decision_explanation_panel(scores, decision_results, analysis_results, portfolio_risk, beginner_mode=context.beginner_mode)
        render_score_cards(scores, beginner_mode=context.beginner_mode)
        render_candidate_stocks(screen_today_candidates(limit=8))
        render_portfolio_summary(positions, metrics, context.cash.total_cash_krw)

    with st.expander(K_INPUT_TITLE, expanded=bool(st.session_state.get("focus_portfolio_input", False))):
        edited_portfolio = render_portfolio_input(get_sample_portfolio())
        _, input_errors = validate_portfolio(edited_portfolio)
        render_portfolio_errors([error for error in input_errors if error not in errors])

    if context.beginner_mode:
        render_terms_help(expanded=False)
    else:
        render_advanced_raw_data(context.selected_menu, market_overview, analysis_results, decision_results)


def render_empty_home(context: PageContext) -> None:
    """Render home dashboard when no portfolio exists."""

    render_brand_header(context.freshness)
    render_disclaimer(context.beginner_mode)
    render_freshness_bar(context.freshness)
    render_morning_brief(context.macro_brief)
    render_onboarding(context.user_mode)
    render_freshness_sidebar(context.freshness)
    render_empty_state()
    render_quick_links()
    with st.expander(K_INPUT_TITLE, expanded=True):
        edited_portfolio = render_portfolio_input(get_sample_portfolio())
        _, input_errors = validate_portfolio(edited_portfolio)
        render_portfolio_errors(input_errors)
    if context.beginner_mode:
        render_terms_help(expanded=False)


def render_market_snapshot(context: PageContext) -> None:
    """Render macro snapshot without the detailed market briefing page."""

    render_morning_brief(context.macro_brief)
    render_macro_market_cards(context.macro_brief.overview)
    render_macro_mini_charts(context.macro_brief.dashboard)
    render_fear_greed_placeholder(context.sentiment)
    render_market_issues_placeholder()


def render_quick_links() -> None:
    """Render quick navigation cards for major menus."""

    st.markdown("### 주요 메뉴 바로가기")
    cols = st.columns(4)
    links = [
        ("종목 판단 보기", "개별 종목 검색과 상세 판단"),
        ("시장 주도주", "시총/거래대금 상위 종목"),
        ("테마 레이더", "테마 강도와 Demo 뉴스"),
        ("포트폴리오 관리", "보유종목과 JSON 관리"),
    ]
    for col, (menu, description) in zip(cols, links, strict=True):
        with col.container(border=True):
            st.markdown(f"**{menu}**")
            st.caption(description)
            if st.button("이동", key=f"home_quick_{menu}", width="stretch"):
                st.session_state["selected_menu"] = menu
                st.rerun()


def render_advanced_raw_data(selected_menu: str, market_overview: pd.DataFrame, analysis_results: pd.DataFrame, decision_results: pd.DataFrame) -> None:
    """Render advanced raw data tables."""

    with st.expander("Advanced raw data", expanded=False):
        st.caption(f"Selected menu: {selected_menu}")
        st.write("Market")
        st.dataframe(market_overview, width="stretch", hide_index=True)
        st.write("Analysis")
        st.dataframe(analysis_results, width="stretch", hide_index=True)
        st.write("Decision")
        st.dataframe(decision_results, width="stretch", hide_index=True)
