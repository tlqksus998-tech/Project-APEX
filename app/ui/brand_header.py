from __future__ import annotations

import streamlit as st

from modules.config.version import APP_NAME, APP_VERSION, BUILD_NAME
from modules.data_freshness import DataFreshnessSnapshot, format_timestamp


def render_brand_header(snapshot: DataFreshnessSnapshot) -> None:
    """Render a premium SaaS hero header."""

    st.markdown(
        f"""
        <div class="apex-hero">
          <div style="display:flex; justify-content:space-between; gap:18px; align-items:flex-start; flex-wrap:wrap;">
            <div>
              <h1>{APP_NAME}</h1>
              <div class="subtitle">AI Portfolio Expert · {BUILD_NAME}</div>
              <div class="meta">데이터 기준 {format_timestamp(snapshot.data_updated_at)} · 가격 {format_timestamp(snapshot.price_updated_at)} · 환율 {format_timestamp(snapshot.fx_updated_at)}</div>
            </div>
            <div style="text-align:right; min-width:220px;">
              <div style="font-size:15px; font-weight:800; margin-bottom:10px;">{APP_VERSION}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
