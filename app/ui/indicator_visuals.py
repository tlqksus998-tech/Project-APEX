from __future__ import annotations

import streamlit as st


def get_rsi_label(rsi_value: float | None) -> str:
    """Return a beginner-friendly RSI status label."""

    value = normalize_rsi(rsi_value)
    if value is None:
        return "데이터 부족"
    if value < 30:
        return "과매도권"
    if value < 40:
        return "반등 관찰"
    if value <= 60:
        return "중립"
    if value <= 70:
        return "강세"
    return "과열 주의"


def get_rsi_description(rsi_value: float | None) -> str:
    """Return a plain Korean explanation for an RSI value."""

    label = get_rsi_label(rsi_value)
    descriptions = {
        "데이터 부족": "RSI 데이터가 부족합니다. 가격 데이터가 더 쌓인 뒤 다시 확인하세요.",
        "과매도권": "주가가 단기적으로 많이 밀린 구간입니다. 반등 가능성도 있지만 추가 하락 위험도 함께 봐야 합니다.",
        "반등 관찰": "하락 후 회복을 시도할 수 있는 구간입니다. 실제 가격 반등과 거래량을 함께 확인하세요.",
        "중립": "지금은 과열도 과매도도 아닌 상태입니다. 방향이 확인될 때까지 관찰이 중요합니다.",
        "강세": "단기 흐름이 강한 편입니다. 다만 과열 구간으로 넘어가는지 확인해야 합니다.",
        "과열 주의": "단기적으로 많이 오른 상태일 수 있습니다. 추격매수는 조심하는 편이 좋습니다.",
    }
    return descriptions[label]


def render_rsi_gauge(rsi_value: float | None) -> None:
    """Render an RSI gauge using Streamlit-native components."""

    value = normalize_rsi(rsi_value)
    label = get_rsi_label(rsi_value)
    description = get_rsi_description(rsi_value)

    with st.container(border=True):
        st.markdown("#### RSI 쉬운 해석")
        if value is None:
            st.warning(description)
            return
        st.metric("RSI", f"{value:.1f}", help="RSI는 주가가 단기적으로 너무 많이 올랐는지, 많이 내려왔는지 보는 지표입니다.")
        st.progress(value / 100.0)
        cols = st.columns(5)
        labels = ["과매도권", "반등 관찰", "중립", "강세", "과열 주의"]
        for col, item in zip(cols, labels, strict=True):
            marker = "**" if item == label else ""
            col.caption(f"{marker}{item}{marker}")
        st.info(f"현재 RSI는 {label} 구간입니다. {description}")


def normalize_rsi(rsi_value: float | None) -> float | None:
    """Return RSI in the 0-100 range or None when unavailable."""

    try:
        value = float(rsi_value)
    except (TypeError, ValueError):
        return None
    if value != value:
        return None
    return max(0.0, min(100.0, value))
