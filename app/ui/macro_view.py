from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.data_freshness import format_timestamp
from modules.market.macro_models import MacroBriefResult, MacroDashboard
from modules.market.sentiment_provider import SentimentIndicator
from modules.utils import format_percent


def render_morning_brief(brief: MacroBriefResult) -> None:
    """Render APEX Morning Brief with macro score and traffic light."""

    dashboard = brief.dashboard
    success_count = dashboard.success_count if dashboard else 0
    failed_count = dashboard.failed_count if dashboard else 0
    with st.container(border=True):
        st.subheader("APEX Morning Brief")
        col1, col2, col3, col4 = st.columns([0.22, 0.24, 0.34, 0.20], vertical_alignment="center")
        col1.metric("APEX Macro Score", f"{brief.macro_score:.1f}")
        col2.metric("Market Signal", brief.traffic_light)
        col3.write(brief.market_status)
        col3.caption("Rule-based macro signal. 매수/매도 지시가 아닙니다.")
        col4.metric("지표 상태", f"{success_count} OK / {failed_count} 실패")
        col4.caption(f"기준: {format_timestamp(brief.updated_at)}")


def render_macro_market_cards(overview: pd.DataFrame) -> None:
    """Render compact macro market metric cards."""

    st.subheader("Macro Market Cards")
    if overview is None or overview.empty:
        st.info("시장 데이터를 아직 표시할 수 없습니다.")
        return

    rows = overview.to_dict(orient="records")
    for start in range(0, len(rows), 4):
        cols = st.columns(4)
        for col, row in zip(cols, rows[start:start + 4]):
            value = float(row.get("current_value", 0.0) or 0.0)
            daily = float(row.get("daily_return", 0.0) or 0.0)
            status = str(row.get("status", ""))
            source = str(row.get("source", ""))
            label = str(row.get("name", ""))
            updated_at = row.get("updated_at")
            icon = "●" if status == "OK" else "△"
            display_value = f"{value:,.2f}" if label in {"USD/KRW", "VIX", "Gold", "WTI"} else f"{value:,.0f}"
            col.metric(f"{icon} {label}", display_value, format_percent(daily))
            col.caption(f"{format_timestamp(updated_at)} 기준 · {source}")


def render_fear_greed_placeholder(sentiment: SentimentIndicator) -> None:
    """Render a placeholder card for future Fear & Greed API integration."""

    with st.container(border=True):
        cols = st.columns([0.35, 0.25, 0.40], vertical_alignment="center")
        cols[0].subheader(sentiment.name)
        cols[1].metric("Status", sentiment.value)
        cols[2].markdown(f"**{sentiment.label}**")
        cols[2].caption("Demo placeholder · 실제 CNN API 미연동")
