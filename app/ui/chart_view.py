from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.design_system import section_title

try:
    import plotly.express as px
except Exception:  # pragma: no cover - cloud dependency fallback
    px = None

from modules.market.macro_models import MacroDashboard
from modules.market.macro_provider import CHART_INSTRUMENTS


def render_macro_mini_charts(macro_data: MacroDashboard | dict[str, pd.DataFrame]) -> None:
    """Render mini charts for core macro instruments with range selection."""

    section_title("주요 지표 차트", "1개월/6개월 흐름을 카드별로 비교합니다.")
    selected_range = st.segmented_control("Chart Range", ["1개월", "6개월"], default="1개월", key="macro_chart_range")
    chart_key = "6mo" if selected_range == "6개월" else "1mo"
    cols = st.columns(2)
    for index, name in enumerate(CHART_INSTRUMENTS):
        history = get_chart_history(macro_data, name, chart_key)
        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                if history.empty:
                    st.info("차트 데이터 조회 실패")
                    continue
                render_line_chart(history)


def render_line_chart(history: pd.DataFrame) -> None:
    """Render a line chart with Plotly when available and Streamlit fallback otherwise."""

    chart_data = history[["date", "close"]].dropna().copy()
    if chart_data.empty:
        st.info("차트 데이터 조회 실패")
        return
    if px is not None:
        fig = px.line(chart_data, x="date", y="close", height=220)
        fig.update_layout(margin=dict(l=8, r=8, t=8, b=8), xaxis_title=None, yaxis_title=None, showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        return
    fallback = chart_data.set_index("date")["close"]
    st.line_chart(fallback, height=220)
    st.caption("Plotly를 사용할 수 없어 기본 Streamlit 차트로 표시합니다.")


def get_chart_history(macro_data: MacroDashboard | dict[str, pd.DataFrame], name: str, chart_key: str) -> pd.DataFrame:
    """Return requested chart history from MacroDashboard or legacy history dict."""

    if isinstance(macro_data, MacroDashboard):
        for indicator in macro_data.indicators:
            if indicator.name == name:
                return indicator.chart_data.get(chart_key, pd.DataFrame())
        return pd.DataFrame()
    return macro_data.get(name, pd.DataFrame()) if macro_data else pd.DataFrame()

