from __future__ import annotations

import streamlit as st


def get_rsi_label(rsi_value: float | None) -> str:
    """Return a beginner-friendly RSI status label."""

    value = normalize_rsi(rsi_value)
    if value is None:
        return "데이터 부족"
    if value < 30:
        return "많이 내려왔어요"
    if value < 40:
        return "반등을 볼 자리예요"
    if value <= 60:
        return "차분한 편이에요"
    if value <= 70:
        return "힘이 있어요"
    return "조금 뜨거워요"


def get_rsi_description(rsi_value: float | None) -> str:
    """Return a plain Korean explanation for an RSI value."""

    label = get_rsi_label(rsi_value)
    descriptions = {
        "데이터 부족": "가격 데이터가 부족해요. 조금 뒤 다시 확인해 보세요.",
        "많이 내려왔어요": "많이 내려온 자리예요. 반등할 수도 있지만 더 흔들릴 수도 있어요.",
        "반등을 볼 자리예요": "조금씩 회복하는지 지켜볼 수 있는 자리예요.",
        "차분한 편이에요": "아직 너무 많이 오른 상태는 아니에요.",
        "힘이 있어요": "오르는 힘이 있지만 너무 뜨거워지는지 봐야 해요.",
        "조금 뜨거워요": "급하게 사기보다는 조심해서 보는 편이 좋아요.",
    }
    return descriptions[label]


def render_rsi_gauge(rsi_value: float | None) -> None:
    """Render an RSI gauge using Streamlit-native components."""

    value = normalize_rsi(rsi_value)
    label = get_rsi_label(rsi_value)
    description = get_rsi_description(rsi_value)

    with st.container(border=True):
        st.markdown("#### 가격 온도")
        if value is None:
            st.warning(description)
            return
        st.metric("상태", label)
        st.progress(value / 100.0)
        cols = st.columns(5)
        labels = ["많이 내려왔어요", "반등을 볼 자리예요", "차분한 편이에요", "힘이 있어요", "조금 뜨거워요"]
        for col, item in zip(cols, labels, strict=True):
            marker = "**" if item == label else ""
            col.caption(f"{marker}{item}{marker}")
        st.info(description)


def normalize_rsi(rsi_value: float | None) -> float | None:
    """Return RSI in the 0-100 range or None when unavailable."""

    try:
        value = float(rsi_value)
    except (TypeError, ValueError):
        return None
    if value != value:
        return None
    return max(0.0, min(100.0, value))
