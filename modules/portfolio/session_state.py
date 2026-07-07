from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.portfolio.input_data import PORTFOLIO_COLUMNS, normalize_portfolio
from modules.portfolio.storage import load_portfolio_json

PORTFOLIO_STATE_KEY = "portfolio_df"


def empty_portfolio() -> pd.DataFrame:
    """Return an empty portfolio DataFrame using the app schema."""

    return pd.DataFrame(columns=PORTFOLIO_COLUMNS)


def initialize_portfolio_state(sample_df: pd.DataFrame | None = None) -> None:
    """Initialize Streamlit portfolio state once per browser session, loading saved JSON when available."""

    if PORTFOLIO_STATE_KEY in st.session_state:
        return
    saved, error = load_portfolio_json()
    if not saved.empty:
        st.session_state[PORTFOLIO_STATE_KEY] = saved
        st.session_state.setdefault("portfolio_storage_notice", "Saved portfolio loaded.")
        return
    initial = empty_portfolio() if sample_df is None else normalize_portfolio(sample_df).head(0)
    st.session_state[PORTFOLIO_STATE_KEY] = initial
    if error and "No saved portfolio" not in error:
        st.session_state.setdefault("portfolio_storage_notice", error)


def get_portfolio_state() -> pd.DataFrame:
    """Return the current session portfolio as a DataFrame."""

    value = st.session_state.get(PORTFOLIO_STATE_KEY)
    if isinstance(value, pd.DataFrame):
        return normalize_portfolio(value)
    return empty_portfolio()


def set_portfolio_state(portfolio: pd.DataFrame | None) -> None:
    """Store a normalized portfolio DataFrame in Streamlit session state."""

    st.session_state[PORTFOLIO_STATE_KEY] = normalize_portfolio(portfolio)


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

