from __future__ import annotations

import pandas as pd
import streamlit as st


def render_analysis_results(analysis_results: pd.DataFrame, market_overview: pd.DataFrame) -> None:
    """Render technical analysis results."""

    st.subheader("Analysis Engine")
    if analysis_results.empty:
        st.info("No OHLCV data available for technical analysis.")
        return

    display = analysis_results.copy()
    if not market_overview.empty:
        display = display.merge(market_overview[["ticker", "current_price"]], on="ticker", how="left")
    else:
        display["current_price"] = None

    numeric_columns = [
        "rsi_14",
        "ma20",
        "ma60",
        "ma120",
        "macd",
        "macd_signal",
        "macd_histogram",
        "volume_ratio",
        "week52_position",
        "current_price",
    ]
    for column in numeric_columns:
        if column in display.columns:
            display[column] = display[column].map(lambda value: None if pd.isna(value) else round(float(value), 2))

    columns = [
        "ticker",
        "current_price",
        "rsi_14",
        "ma20",
        "ma60",
        "ma120",
        "trend_status",
        "macd_status",
        "volume_status",
        "volume_ratio",
        "week52_position",
        "success",
        "message",
    ]
    st.dataframe(display[columns], width="stretch", hide_index=True)
