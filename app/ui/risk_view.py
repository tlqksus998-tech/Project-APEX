from __future__ import annotations

import pandas as pd
import streamlit as st


def render_risk_panel(risk_results: list[dict[str, str]]) -> None:
    """Render legacy risk result messages."""

    st.subheader("Risk Panel")
    for alert in risk_results:
        message = f"**{alert['title']}**\n\n{alert['message']}"
        if alert["level"] == "danger":
            st.error(message)
        elif alert["level"] == "warning":
            st.warning(message)
        else:
            st.info(message)


def render_portfolio_risk_panel(portfolio_risk: pd.DataFrame) -> None:
    """Render portfolio risk adjustment messages."""

    st.subheader("Portfolio Risk Adjustment")
    if portfolio_risk.empty:
        st.info("No portfolio risk results available.")
        return

    total_penalty = float(portfolio_risk["total_risk_penalty"].sum())
    st.metric("Total Risk Penalty", f"{total_penalty:.1f}")

    for _, row in portfolio_risk.iterrows():
        messages = row.get("risk_messages", [])
        if not messages:
            st.success(f"{row['ticker']}: Normal")
            continue
        st.warning(f"{row['ticker']}: " + " | ".join(messages))
