from __future__ import annotations

import streamlit as st

from app.ui.brand_header import render_brand_header
from app.ui.freshness_view import render_freshness_bar, render_freshness_sidebar
from app.ui.help_text import render_terms_help
from app.ui.page_context import PageContext
from app.ui.pro_gate_view import render_disclaimer
from modules.settings import APP_SETTINGS


def render_settings_page(context: PageContext) -> None:
    """Render settings and defaults page."""

    render_brand_header(context.freshness)
    render_disclaimer(context.beginner_mode)
    render_freshness_bar(context.freshness)
    st.subheader("설정")
    st.info("View Mode, Market Controls, Cash / Currency 입력은 사이드바에서 관리합니다.")
    st.json(APP_SETTINGS)
    render_terms_help(expanded=True)
    render_freshness_sidebar(context.freshness)
