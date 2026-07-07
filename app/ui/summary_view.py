from __future__ import annotations

import streamlit as st

from app.ui.design_system import badge, section_title
from modules.summary.summary_models import PortfolioSummaryResult

K_TITLE = "AI 포트폴리오 종합 총평"
K_DECISION = "Overall Decision"
K_SCORE = "Overall Score"
K_RISK = "Risk Level"
K_CONFIDENCE = "Confidence"
K_STRENGTHS = "핵심 강점"
K_RISKS = "핵심 리스크"
K_ACTIONS = "오늘의 행동"


def render_portfolio_ai_summary(summary: PortfolioSummaryResult) -> None:
    """Render the portfolio-level rule-based AI summary card."""

    section_title(K_TITLE, "내 포트폴리오를 한 문장으로 먼저 이해합니다.")
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(badge(summary.overall_decision), unsafe_allow_html=True)
        col1.caption(K_DECISION)
        col2.metric(K_SCORE, f"{summary.overall_score:.1f}")
        col3.markdown(badge(f"{summary.risk_level} Risk"), unsafe_allow_html=True)
        col3.caption(K_RISK)
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
