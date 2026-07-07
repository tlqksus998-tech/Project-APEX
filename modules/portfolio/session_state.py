from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.portfolio.input_data import PORTFOLIO_COLUMNS, normalize_portfolio

PORTFOLIO_STATE_KEY = "portfolio_df"
LEGACY_PORTFOLIO_STATE_KEY = "portfolio"
KRW_CASH_STATE_KEY = "krw_cash"
USD_CASH_STATE_KEY = "usd_cash"
FX_RATE_STATE_KEY = "fx_rate"
SELECTED_TICKER_STATE_KEY = "selected_ticker"
SELECTED_ANALYSIS_TICKER_STATE_KEY = "selected_analysis_ticker"
APEX_TRACK_STATE_KEY = "apex_track"
EASY_MENU_STATE_KEY = "easy_menu"


def empty_portfolio() -> pd.DataFrame:
    """Return an empty portfolio DataFrame using the app schema."""

    return pd.DataFrame(columns=PORTFOLIO_COLUMNS)


def initialize_runtime_defaults() -> None:
    """Set first-run defaults without injecting sample holdings."""

    st.session_state.setdefault(LEGACY_PORTFOLIO_STATE_KEY, [])
    st.session_state.setdefault(KRW_CASH_STATE_KEY, 0.0)
    st.session_state.setdefault(USD_CASH_STATE_KEY, 0.0)
    st.session_state.setdefault(FX_RATE_STATE_KEY, 1380.0)
    st.session_state.setdefault(SELECTED_TICKER_STATE_KEY, None)
    st.session_state.setdefault(SELECTED_ANALYSIS_TICKER_STATE_KEY, None)
    if st.session_state.get(APEX_TRACK_STATE_KEY) not in {"쉽게 보기", "개발자 모드"}:
        st.session_state[APEX_TRACK_STATE_KEY] = "쉽게 보기"
    if st.session_state.get(EASY_MENU_STATE_KEY) not in {"종목분석", "AI 랭킹"}:
        st.session_state[EASY_MENU_STATE_KEY] = "종목분석"


def sync_legacy_portfolio_state(portfolio: pd.DataFrame | None) -> None:
    """Mirror the DataFrame portfolio to the legacy list-based state key."""

    cleaned = normalize_portfolio(portfolio)
    st.session_state[LEGACY_PORTFOLIO_STATE_KEY] = cleaned.to_dict(orient="records")


def initialize_portfolio_state(sample_df: pd.DataFrame | None = None) -> None:
    """Initialize Streamlit portfolio state once per browser session without sample injection."""

    initialize_runtime_defaults()
    if PORTFOLIO_STATE_KEY in st.session_state:
        return
    legacy_value = st.session_state.get(LEGACY_PORTFOLIO_STATE_KEY)
    if isinstance(legacy_value, list) and legacy_value:
        st.session_state[PORTFOLIO_STATE_KEY] = normalize_portfolio(pd.DataFrame(legacy_value))
        sync_legacy_portfolio_state(st.session_state[PORTFOLIO_STATE_KEY])
        return
    st.session_state[PORTFOLIO_STATE_KEY] = empty_portfolio()
    sync_legacy_portfolio_state(st.session_state[PORTFOLIO_STATE_KEY])


def get_portfolio_state() -> pd.DataFrame:
    """Return the current session portfolio as a DataFrame."""

    value = st.session_state.get(PORTFOLIO_STATE_KEY)
    if isinstance(value, pd.DataFrame):
        return normalize_portfolio(value)
    return empty_portfolio()


def set_portfolio_state(portfolio: pd.DataFrame | None) -> None:
    """Store a normalized portfolio DataFrame in Streamlit session state."""

    cleaned = normalize_portfolio(portfolio)
    st.session_state[PORTFOLIO_STATE_KEY] = cleaned
    sync_legacy_portfolio_state(cleaned)


def add_holding(name: str, ticker: str, quantity: float, avg_price: float) -> tuple[bool, str]:
    """Add one holding to the session portfolio unless it already exists."""

    if quantity <= 0:
        return False, "Quantity must be greater than zero."
    if avg_price < 0:
        return False, "Average price cannot be negative."

    portfolio = get_portfolio_state()
    new_row = pd.DataFrame(
        [{"name": name, "ticker": ticker, "quantity": float(quantity), "avg_price": float(avg_price)}],
        columns=PORTFOLIO_COLUMNS,
    )
    normalized_row = normalize_portfolio(new_row)
    if normalized_row.empty or not str(normalized_row.iloc[0]["ticker"]).strip():
        return False, "Ticker could not be resolved."

    resolved_ticker = str(normalized_row.iloc[0]["ticker"])
    if not portfolio.empty and resolved_ticker in portfolio["ticker"].astype(str).tolist():
        return False, f"{resolved_ticker} is already in the portfolio."

    updated = pd.concat([portfolio, normalized_row], ignore_index=True)
    set_portfolio_state(updated)
    return True, f"Added {resolved_ticker} to the portfolio."


def remove_holding(ticker: str) -> None:
    """Remove a holding from the session portfolio by ticker."""

    portfolio = get_portfolio_state()
    if portfolio.empty:
        return
    set_portfolio_state(portfolio[portfolio["ticker"].astype(str) != str(ticker)])

