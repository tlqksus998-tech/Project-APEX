from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.design_system import badge, section_title
from modules.data_freshness import format_timestamp
from modules.market.macro_models import MacroBriefResult
from modules.market.sentiment_provider import SentimentIndicator
from modules.utils import format_percent


def render_morning_brief(brief: MacroBriefResult) -> None:
    """Render APEX Morning Brief with macro score and traffic light."""

    dashboard = brief.dashboard
    success_count = dashboard.success_count if dashboard else 0
    failed_count = dashboard.failed_count if dashboard else 0
    section_title("APEX Morning Brief", "오늘 시장 상태를 한눈에 확인하세요.")
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([0.22, 0.24, 0.34, 0.20], vertical_alignment="center")
        col1.metric("APEX Macro Score", f"{brief.macro_score:.1f}")
        col2.markdown(badge(brief.traffic_light), unsafe_allow_html=True)
        col3.write(brief.market_status)
        col3.caption("시장 온도계이며 매수/매도 지시가 아닙니다.")
        col4.metric("지표 상태", f"{success_count} OK / {failed_count} 실패")
        col4.caption(f"기준: {format_timestamp(brief.updated_at)}")


def render_macro_market_cards(overview: pd.DataFrame) -> None:
    """Render compact macro market metric cards."""

    section_title("Macro Market Cards", "주요 시장 지표와 변화를 확인합니다.")
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
            state = "Live" if status == "OK" else "Demo"
            display_value = f"{value:,.2f}" if label in {"USD/KRW", "VIX", "Gold", "WTI"} else f"{value:,.0f}"
            with col.container(border=True):
                st.markdown(badge(state), unsafe_allow_html=True)
                st.metric(label, display_value, format_percent(daily))
                st.caption(f"{format_timestamp(updated_at)} 기준 · {source}")


def render_fear_greed_placeholder(sentiment: SentimentIndicator) -> None:
    """Render a placeholder card for future Fear & Greed API integration."""

    section_title("Fear & Greed", "시장 심리 데이터는 아직 Demo 상태입니다.")
    with st.container(border=True):
        cols = st.columns([0.35, 0.25, 0.40], vertical_alignment="center")
        cols[0].subheader(sentiment.name)
        cols[1].metric("Status", sentiment.value)
        cols[2].markdown(badge("Placeholder"), unsafe_allow_html=True)
        cols[2].caption("향후 실제 API 연동 예정")
