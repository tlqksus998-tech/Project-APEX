from __future__ import annotations

import pandas as pd
import streamlit as st


def render_decision_results(decision_results: pd.DataFrame) -> None:
    """Render Decision Engine results."""

    st.subheader("Decision Engine")
    if decision_results.empty:
        st.info("No decision results available.")
        return

    display = decision_results.copy()
    for column in ["decision_score", "risk_penalty", "final_score", "confidence_score", "stock_score", "risk_score", "portfolio_fit_score"]:
        if column in display.columns:
            display[column] = display[column].map(lambda value: round(float(value), 1))
    display["reasons"] = display["reasons"].map(lambda reasons: " | ".join(reasons[:3]) if isinstance(reasons, list) else str(reasons))
    display["risk_messages"] = display["risk_messages"].map(lambda messages: " | ".join(messages[:3]) if isinstance(messages, list) else str(messages))
    columns = [
        "ticker",
        "stock_signal",
        "final_decision",
        "decision",
        "decision_score",
        "final_score",
        "confidence_score",
        "market_regime",
        "stock_score",
        "risk_score",
        "portfolio_fit_score",
        "reasons",
        "risk_messages",
    ]
    columns = [column for column in columns if column in display.columns]
    st.dataframe(display[columns], width="stretch", hide_index=True)
