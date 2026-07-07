from __future__ import annotations

import streamlit as st

from app.ui.design_system import badge, section_title

DEMO_ISSUES = [
    "미국 CPI 발표 예정",
    "반도체 업종 강세",
    "환율 변동성 확대",
]


def render_market_issues_placeholder() -> None:
    """Render clearly marked demo market issue cards without a news API."""

    section_title("오늘의 주요 이슈", "실제 뉴스가 아닌 Demo 데이터입니다.")
    with st.container(border=True):
        st.markdown(badge("Demo"), unsafe_allow_html=True)
        for issue in DEMO_ISSUES:
            st.write(f"- {issue}")
        st.caption("실제 뉴스 API는 아직 연동하지 않았습니다.")
