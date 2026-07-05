from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.utils import format_percent


def render_market_data(price_results: pd.DataFrame) -> None:
    """Render current price lookup results."""

    st.subheader("Market Data")
    if price_results.empty:
        st.info("No tickers available for market data.")
        return

    display = price_results.copy()
    if "daily_return" in display.columns:
        display["daily_return"] = display["daily_return"].map(format_percent)
    if "period_return" in display.columns:
        display["period_return"] = display["period_return"].map(format_percent)

    columns = ["ticker", "current_price", "source", "success", "message"]
    optional_columns = ["daily_return", "period_return"]
    selected_columns = columns + [column for column in optional_columns if column in display.columns]
    st.dataframe(display[selected_columns], width="stretch", hide_index=True)


def render_price_history(overview: pd.DataFrame, histories: dict[str, pd.DataFrame]) -> None:
    """Render a lightweight close-price chart for one selected ticker."""

    if overview.empty:
        return

    ticker_options = overview["ticker"].tolist()
    selected_ticker = st.selectbox("Price History", ticker_options)
    history = histories.get(selected_ticker, pd.DataFrame())
    if history.empty:
        st.info("No price history available for the selected ticker.")
        return

    chart_data = history[["date", "close"]].set_index("date")
    st.line_chart(chart_data, y="close", width="stretch")
