import pandas as pd
import streamlit as st

from app.ui.home_view import K_EMPTY_ACTION_GUIDE
from modules.portfolio.calculator import calculate_portfolio_summary
from modules.portfolio.session_state import (
    FX_RATE_STATE_KEY,
    KRW_CASH_STATE_KEY,
    LEGACY_PORTFOLIO_STATE_KEY,
    PORTFOLIO_STATE_KEY,
    SELECTED_ANALYSIS_TICKER_STATE_KEY,
    SELECTED_TICKER_STATE_KEY,
    USD_CASH_STATE_KEY,
    empty_portfolio,
    initialize_portfolio_state,
)
from modules.portfolio.storage import load_portfolio_json_bytes, portfolio_to_json_bytes
from modules.summary.portfolio_summary import generate_portfolio_summary


def _clear_state() -> None:
    """Clear Streamlit state in test mode."""

    for key in list(st.session_state.keys()):
        del st.session_state[key]


def test_initial_portfolio_state_is_empty():
    _clear_state()

    initialize_portfolio_state()

    assert st.session_state[LEGACY_PORTFOLIO_STATE_KEY] == []
    assert st.session_state[PORTFOLIO_STATE_KEY].empty
    assert st.session_state[KRW_CASH_STATE_KEY] == 0.0
    assert st.session_state[USD_CASH_STATE_KEY] == 0.0
    assert st.session_state[FX_RATE_STATE_KEY] == 1380.0
    assert st.session_state[SELECTED_TICKER_STATE_KEY] is None
    assert st.session_state[SELECTED_ANALYSIS_TICKER_STATE_KEY] is None


def test_sample_holdings_are_not_auto_injected():
    _clear_state()

    initialize_portfolio_state()

    tickers = st.session_state[PORTFOLIO_STATE_KEY].get("ticker", pd.Series(dtype=str)).astype(str).tolist()
    assert tickers == []
    assert not {"KORU", "MU", "000660", "360200"}.intersection(tickers)


def test_existing_session_portfolio_is_preserved():
    _clear_state()
    st.session_state[LEGACY_PORTFOLIO_STATE_KEY] = [{"name": "Apple", "ticker": "AAPL", "quantity": 1, "avg_price": 100}]

    initialize_portfolio_state()

    assert st.session_state[PORTFOLIO_STATE_KEY].iloc[0]["ticker"] == "AAPL"
    assert st.session_state[LEGACY_PORTFOLIO_STATE_KEY][0]["ticker"] == "AAPL"


def test_empty_portfolio_summary_calculation_is_safe():
    positions, metrics = calculate_portfolio_summary(empty_portfolio(), pd.DataFrame())

    assert positions.empty
    assert metrics["total_invested"] == 0.0
    assert metrics["total_current_value"] == 0.0
    assert metrics["profit_loss"] == 0.0
    assert metrics["return_rate"] == 0.0


def test_empty_portfolio_ai_summary_and_action_guide_are_safe():
    summary = generate_portfolio_summary({}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 0.0)

    assert summary.summary_text
    assert summary.overall_score == 0.0
    assert "보유종목이 없어" in K_EMPTY_ACTION_GUIDE


def test_portfolio_json_round_trip_still_works():
    portfolio = pd.DataFrame([{"name": "Apple", "ticker": "AAPL", "quantity": 2, "avg_price": 100}])

    content, error = portfolio_to_json_bytes(portfolio)
    loaded, load_error = load_portfolio_json_bytes(content or b"")

    assert error is None
    assert load_error is None
    assert loaded.iloc[0]["ticker"] == "AAPL"
