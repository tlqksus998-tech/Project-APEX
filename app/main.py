from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from app.ui.candidate_view import render_candidate_stocks
from app.ui.help_text import render_terms_help
from app.ui.onboarding import render_empty_state, render_onboarding
from app.ui.portfolio_view import render_portfolio_errors, render_portfolio_input
from app.ui.sidebar import render_cash_input, render_market_controls, render_sidebar, render_user_mode
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
    render_today_title,
)
from modules.analysis import analyze_many
from modules.config import get_config
from modules.decision import decide_many
from modules.market import build_market_overview
from modules.portfolio.calculator import calculate_portfolio_summary
from modules.portfolio.input_data import get_sample_portfolio, validate_portfolio
from modules.portfolio.session_state import get_portfolio_state, initialize_portfolio_state
from modules.risk import evaluate_portfolio_risk
from modules.screening import screen_today_candidates


K_PAGE_TITLE = "\uc624\ub298\uc758 \ud22c\uc790\ud310\ub2e8"
K_INPUT_TITLE = "\ud3ec\ud2b8\ud3f4\ub9ac\uc624 \uc785\ub825/\uc218\uc815"
K_LOADING = "\uc2dc\uc7a5 \ub370\uc774\ud130\uc640 \ub9ac\uc2a4\ud06c\ub97c \ubd84\uc11d\ud558\ub294 \uc911\uc785\ub2c8\ub2e4..."
K_ENGINE_ERROR = "\uac00\uaca9 \ub610\ub294 \ubd84\uc11d \ub370\uc774\ud130\ub97c \uac00\uc838\uc624\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4. \ud2f0\ucee4\ub97c \ud655\uc778\ud558\uac70\ub098 \uc7a0\uc2dc \ud6c4 \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694."


def prices_from_market_overview(overview: pd.DataFrame) -> pd.DataFrame:
    """Convert market overview rows into portfolio price rows."""

    if overview.empty:
        return pd.DataFrame(columns=["ticker", "current_price", "price_source"])
    return overview[["ticker", "current_price", "source"]].rename(columns={"source": "price_source"})


def run_dashboard_engines(portfolio: pd.DataFrame, cash_amount: float, period: str, interval: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float], pd.DataFrame]:
    """Run market, analysis, decision, and risk engines with a friendly fallback."""

    try:
        config = get_config()
        tickers = portfolio["ticker"].tolist() if not portfolio.empty else []
        market_overview, histories = build_market_overview(tickers, config, period=period, interval=interval)
        analysis_results = analyze_many(histories)
        positions, metrics = calculate_portfolio_summary(portfolio, prices_from_market_overview(market_overview))
        portfolio_risk = evaluate_portfolio_risk(positions, cash_amount=cash_amount)
        decision_results = decide_many(analysis_results, portfolio_risk)
        return market_overview, analysis_results, positions, portfolio_risk, metrics, decision_results
    except Exception:
        st.warning(K_ENGINE_ERROR)
        empty_metrics = {"total_invested": 0.0, "total_current_value": 0.0, "profit_loss": 0.0, "return_rate": 0.0}
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), empty_metrics, pd.DataFrame()


def main() -> None:
    """Run the Project APEX Today Dashboard."""

    st.set_page_config(page_title=K_PAGE_TITLE, layout="wide")
    initialize_portfolio_state(get_sample_portfolio())

    selected_menu = render_sidebar()
    user_mode = render_user_mode()
    beginner_mode = user_mode == "beginner"
    period, interval = render_market_controls()
    cash_amount = render_cash_input()

    render_today_title()
    render_onboarding(user_mode)

    portfolio, errors = validate_portfolio(get_portfolio_state())
    if portfolio.empty:
        render_empty_state()
        with st.expander(K_INPUT_TITLE, expanded=True):
            edited_portfolio = render_portfolio_input(get_sample_portfolio())
            _, input_errors = validate_portfolio(edited_portfolio)
            render_portfolio_errors(input_errors)
        if beginner_mode:
            render_terms_help(expanded=False)
        return

    with st.spinner(K_LOADING):
        market_overview, analysis_results, positions, portfolio_risk, metrics, decision_results = run_dashboard_engines(portfolio, cash_amount, period, interval)

    scores = compute_dashboard_scores(decision_results, portfolio_risk)
    actions = build_today_actions(positions, portfolio_risk, scores)
    dashboard_table = build_dashboard_table(positions, analysis_results, decision_results, portfolio_risk)
    candidates = screen_today_candidates(limit=8)

    render_decision_explanation_panel(scores, decision_results, analysis_results, portfolio_risk, beginner_mode=beginner_mode)
    render_score_cards(scores, beginner_mode=beginner_mode)
    render_action_card(actions)
    render_candidate_stocks(candidates)
    render_risk_alerts(portfolio_risk)
    render_portfolio_summary(positions, metrics, cash_amount)
    render_dashboard_table(dashboard_table, beginner_mode=beginner_mode)

    with st.expander(K_INPUT_TITLE, expanded=bool(st.session_state.get("focus_portfolio_input", False))):
        edited_portfolio = render_portfolio_input(get_sample_portfolio())
        _, input_errors = validate_portfolio(edited_portfolio)
        render_portfolio_errors([error for error in input_errors if error not in errors])

    if beginner_mode:
        render_terms_help(expanded=False)
    else:
        with st.expander("Advanced raw data", expanded=False):
            st.caption(f"Selected menu: {selected_menu}")
            st.write("Market")
            st.dataframe(market_overview, width="stretch", hide_index=True)
            st.write("Analysis")
            st.dataframe(analysis_results, width="stretch", hide_index=True)
            st.write("Decision")
            st.dataframe(decision_results, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
