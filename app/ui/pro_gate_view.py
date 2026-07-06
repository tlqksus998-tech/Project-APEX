from __future__ import annotations

import streamlit as st

from modules.config.app_tier import get_app_tier

PRO_BENEFITS = [
    "보유종목 무제한",
    "통화별 노출 분석",
    "섹터별 중복투자 경고",
    "추가매수 승인/보류 판단",
]


def render_pro_locked_card(title: str, description: str) -> None:
    """Render a locked feature card for Pro tier."""

    with st.container(border=True):
        st.markdown(f"### 🔒 {title}")
        st.write(description)
        st.caption("이 기능은 Pro 버전에서 제공됩니다.")
        st.markdown("**Pro에서는**")
        for benefit in PRO_BENEFITS:
            st.write(f"- {benefit}")


def render_upgrade_hint(feature_name: str) -> None:
    """Render a short upgrade hint for one gated feature."""

    st.info(f"{feature_name} 기능은 Pro 버전에서 제공됩니다. 현재 플랜: {get_app_tier()}")


def render_disclaimer(beginner_mode: bool = True) -> None:
    """Render investment disclaimer text."""

    if beginner_mode:
        st.caption("APEX는 종목을 대신 사라고 지시하지 않습니다. 오늘 살펴볼 만한 후보와 주의할 점을 알려주는 도구입니다.")
    else:
        st.caption("본 서비스는 투자 판단을 돕기 위한 정보 제공 도구입니다. 표시되는 관심 후보는 매수 지시가 아니며, 최종 투자 결정과 책임은 사용자 본인에게 있습니다.")
