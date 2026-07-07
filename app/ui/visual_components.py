from __future__ import annotations

import streamlit as st


def render_score_bar(label: str, score: float, left: str = "낮음", right: str = "높음") -> None:
    """Render a simple score bar."""

    safe_score = max(0.0, min(100.0, float(score)))
    st.markdown(f"**{label}**")
    st.progress(safe_score / 100.0)
    col_left, col_score, col_right = st.columns([0.3, 0.4, 0.3])
    col_left.caption(left)
    col_score.markdown(f"<div style='text-align:center;font-weight:800'>{safe_score:.0f}점</div>", unsafe_allow_html=True)
    col_right.caption(right)


def render_position_bar(label: str, value: float | None, left: str = "싸요", right: str = "비싸요") -> None:
    """Render a position bar for 0-100 values."""

    if value is None:
        st.info(f"{label}: 아직 판단하기 어려워요.")
        return
    safe_value = max(0.0, min(100.0, float(value)))
    st.markdown(f"**{label}**")
    st.progress(safe_value / 100.0)
    col_left, col_mid, col_right = st.columns([0.25, 0.5, 0.25])
    col_left.caption(left)
    col_mid.markdown(f"<div style='text-align:center'>현재 위치 {safe_value:.0f}</div>", unsafe_allow_html=True)
    col_right.caption(right)


def render_meaning_row(label: str, value: str) -> None:
    """Render one simple meaning row."""

    with st.container(border=True):
        st.markdown(f"**{label}**")
        st.write(value)
