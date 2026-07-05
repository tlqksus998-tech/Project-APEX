from __future__ import annotations

import streamlit as st

from modules.summary.summary_models import PortfolioSummaryResult

K_TITLE = "AI \ud3ec\ud2b8\ud3f4\ub9ac\uc624 \uc885\ud569 \ucd1d\ud3c9"
K_DECISION = "Overall Decision"
K_SCORE = "Overall Score"
K_RISK = "Risk Level"
K_CONFIDENCE = "Confidence"
K_STRENGTHS = "\ud575\uc2ec \uac15\uc810"
K_RISKS = "\ud575\uc2ec \ub9ac\uc2a4\ud06c"
K_ACTIONS = "\uc624\ub298\uc758 \ud589\ub3d9"

RISK_COLORS = {
    "Low": "#dcfce7",
    "Medium": "#fef3c7",
    "High": "#fee2e2",
}


def render_portfolio_ai_summary(summary: PortfolioSummaryResult) -> None:
    """Render the portfolio-level rule-based AI summary card."""

    with st.container(border=True):
        st.subheader(K_TITLE)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(K_DECISION, summary.overall_decision)
        col2.metric(K_SCORE, f"{summary.overall_score:.1f}")
        col3.metric(K_RISK, summary.risk_level)
        col4.metric(K_CONFIDENCE, f"{summary.confidence:.0f}%")
        st.write(summary.summary_text)

        col_strength, col_risk, col_action = st.columns(3)
        with col_strength:
            st.markdown(f"**{K_STRENGTHS}**")
            for item in summary.key_strengths:
                st.write(f"- {item}")
        with col_risk:
            st.markdown(f"**{K_RISKS}**")
            for item in summary.key_risks:
                st.write(f"- {item}")
        with col_action:
            st.markdown(f"**{K_ACTIONS}**")
            for item in summary.action_items:
                st.write(f"- {item}")
