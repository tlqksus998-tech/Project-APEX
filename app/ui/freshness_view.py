from __future__ import annotations

import streamlit as st

from modules.config.version import APP_NAME, APP_VERSION, BUILD_DATE, BUILD_NAME
from modules.data_freshness import DataFreshnessSnapshot, format_timestamp


def render_product_header(snapshot: DataFreshnessSnapshot | None = None) -> None:
    """Render a polished product header for the Home dashboard."""

    data_basis = format_timestamp(snapshot.data_updated_at) if snapshot else "분석 전"
    st.markdown(f"## {APP_NAME} {APP_VERSION}")
    st.caption(f"{BUILD_NAME} | Last Updated: {BUILD_DATE} | 데이터 기준: {data_basis}")


def render_freshness_bar(snapshot: DataFreshnessSnapshot) -> None:
    """Render compact freshness metrics for market, FX, and analysis data."""

    st.caption("데이터 기준 시간")
    cols = st.columns(5)
    cols[0].metric("데이터 기준", format_timestamp(snapshot.data_updated_at))
    cols[1].metric("가격 데이터", "최근 조회 완료" if snapshot.price_updated_at else "조회 전")
    cols[2].metric("환율", f"{snapshot.fx_rate:,.1f}원", help=f"{format_timestamp(snapshot.fx_updated_at)} 기준 / {snapshot.fx_source}")
    cols[3].metric("KRX 종목DB", format_timestamp(snapshot.krx_master_updated_at, date_only=True))
    cols[4].metric("AI 분석", format_analysis_time(snapshot))


def render_freshness_sidebar(snapshot: DataFreshnessSnapshot) -> None:
    """Render freshness information in the sidebar."""

    st.sidebar.divider()
    st.sidebar.caption("Data Freshness")
    st.sidebar.caption(f"데이터 기준: {format_timestamp(snapshot.data_updated_at)}")
    st.sidebar.caption(f"환율: {snapshot.fx_rate:,.1f}원 / {format_timestamp(snapshot.fx_updated_at)}")
    st.sidebar.caption(f"KRX 종목DB: {format_timestamp(snapshot.krx_master_updated_at, date_only=True)}")
    st.sidebar.caption(f"AI 분석: {format_analysis_time(snapshot)}")


def format_analysis_time(snapshot: DataFreshnessSnapshot) -> str:
    """Return short analysis runtime label."""

    if snapshot.analysis_run_at is None:
        return "실행 전"
    return snapshot.analysis_run_at.strftime("%H:%M 실행")
