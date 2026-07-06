from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.market.macro_models import MacroDashboard
from modules.market.macro_provider import CHART_INSTRUMENTS


def render_macro_mini_charts(macro_data: MacroDashboard | dict[str, pd.DataFrame]) -> None:
    """Render mini charts for core macro instruments with range selection."""

    st.subheader("주요 지표 차트")
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
                fig = px.line(history, x="date", y="close", height=220)
                fig.update_layout(margin=dict(l=8, r=8, t=8, b=8), xaxis_title=None, yaxis_title=None, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def get_chart_history(macro_data: MacroDashboard | dict[str, pd.DataFrame], name: str, chart_key: str) -> pd.DataFrame:
    """Return requested chart history from MacroDashboard or legacy history dict."""

    if isinstance(macro_data, MacroDashboard):
        for indicator in macro_data.indicators:
            if indicator.name == name:
                return indicator.chart_data.get(chart_key, pd.DataFrame())
        return pd.DataFrame()
    return macro_data.get(name, pd.DataFrame()) if macro_data else pd.DataFrame()
