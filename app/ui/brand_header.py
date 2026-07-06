from __future__ import annotations

import streamlit as st

from modules.config.version import APP_NAME, APP_VERSION, BUILD_DATE, BUILD_NAME
from modules.data_freshness import DataFreshnessSnapshot, format_timestamp


def render_brand_header(snapshot: DataFreshnessSnapshot) -> None:
    """Render the v1.0 style brand header."""

    with st.container(border=True):
        left, right = st.columns([0.68, 0.32], vertical_alignment="center")
        left.markdown(f"# {APP_NAME}")
        left.markdown(f"### {BUILD_NAME}")
        left.caption("v1.0 Beta 준비 버전")
        right.metric("App Version", APP_VERSION)
        right.caption(f"데이터 기준: {format_timestamp(snapshot.data_updated_at)}")
        right.caption(f"가격 조회: {format_timestamp(snapshot.price_updated_at)}")
        right.caption(f"환율 조회: {format_timestamp(snapshot.fx_updated_at)}")
        right.caption(f"분석 실행: {format_timestamp(snapshot.analysis_run_at)}")
        right.caption(f"Build Date: {BUILD_DATE}")
