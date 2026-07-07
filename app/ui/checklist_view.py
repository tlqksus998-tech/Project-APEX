from __future__ import annotations

import streamlit as st

from app.ui.design_system import badge
from modules.analysis.checklist import AnalysisChecklist, ChecklistItem


BADGE_LABELS = {
    "좋음": "Low Risk",
    "보통": "HOLD",
    "중립": "HOLD",
    "관망": "WAIT",
    "주의": "Medium Risk",
    "데이터 부족": "Placeholder",
}


def render_analysis_checklist(checklist: AnalysisChecklist, beginner_mode: bool = True) -> None:
    """Render a beginner-friendly judgement checklist."""

    st.markdown("#### 판단 체크리스트")
    st.caption("전문 지표 이름보다 지금 무엇을 확인해야 하는지 먼저 보여줍니다.")
    with st.container(border=True):
        for item in checklist.items:
            render_checklist_item(item, beginner_mode=beginner_mode)
        st.info(checklist.summary)


def render_checklist_item(item: ChecklistItem, beginner_mode: bool = True) -> None:
    """Render one checklist row."""

    col_label, col_status = st.columns([0.62, 0.38], vertical_alignment="center")
    col_label.markdown(f"**{item.category}**")
    col_status.markdown(badge(BADGE_LABELS.get(item.status, "Placeholder")), unsafe_allow_html=True)
    if beginner_mode:
        st.caption(item.description)
    else:
        st.caption(f"{item.status}: {item.description}")
