from __future__ import annotations

import streamlit as st


def render_disclaimer(beginner_mode: bool = True) -> None:
    """Render investment disclaimer text."""

    if beginner_mode:
        st.caption("APEX는 종목을 대신 사라고 지시하지 않습니다. 오늘 살펴볼 만한 후보와 주의할 점을 알려주는 도구입니다.")
    else:
        st.caption("본 서비스는 투자 판단을 돕기 위한 정보 제공 도구입니다. 표시되는 관심 후보는 매수 지시가 아니며, 최종 투자 결정과 책임은 사용자 본인에게 있습니다.")
