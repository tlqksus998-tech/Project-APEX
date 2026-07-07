from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.design_system import badge, section_title
from app.ui.theme_news_view import render_theme_news
from modules.news.theme_news_provider import get_theme_news
from modules.theme import calculate_all_theme_strengths, calculate_theme_strength, get_theme_assets, list_themes
from modules.utils import format_percent
from modules.data_freshness import format_timestamp


def render_theme_radar() -> None:
    """Render theme strength and theme news intelligence foundation."""

    section_title("테마 레이더", "최근 조회 기준 테마 흐름과 관련 이슈를 확인합니다. 매수 추천이 아닌 참고자료입니다.")
    strengths = calculate_all_theme_strengths()
    render_theme_summary(strengths)

    themes = list_themes()
    selected_theme = st.selectbox("테마 선택", themes, key="theme_radar_selected_theme")
    selected_strength = calculate_theme_strength(selected_theme)
    assets = get_theme_assets(selected_theme)

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("테마", selected_theme)
        col2.markdown(badge(selected_strength.strength_label), unsafe_allow_html=True)
        col3.metric("평균 등락률", format_percent(selected_strength.avg_change_pct))
        col4.metric("상승/하락", f"{selected_strength.positive_count}/{selected_strength.negative_count}")
        st.caption(f"데이터 기준: {format_timestamp(selected_strength.updated_at)} / 출처: {selected_strength.source}")
        if selected_strength.is_fallback:
            st.warning(selected_strength.error_message)
        st.write("관련 종목: " + ", ".join(f"{asset.name}({asset.ticker})" for asset in assets))
        st.info(build_apex_commentary(selected_theme, selected_strength.strength_label))

    render_theme_news(get_theme_news(selected_theme))


def render_theme_summary(strengths: list) -> None:
    """Render all theme strength rows."""

    if not strengths:
        st.info("표시할 테마 데이터가 없습니다.")
        return
    frame = pd.DataFrame([item.__dict__ for item in strengths])
    display = frame[["theme", "avg_change_pct", "positive_count", "negative_count", "total_count", "strength_label", "source", "is_fallback"]].copy()
    display["avg_change_pct"] = display["avg_change_pct"].map(format_percent)
    st.dataframe(display, width="stretch", hide_index=True)


def build_apex_commentary(theme: str, label: str) -> str:
    """Build conservative APEX commentary for theme flow."""

    if "강세" in label:
        return f"{theme} 테마는 최근 관련 종목 평균 흐름이 양호합니다. 다만 포트폴리오 내 해당 테마 비중이 높다면 신규 진입보다 비중 관리가 우선입니다."
    if "약세" in label:
        return f"{theme} 테마는 최근 흐름이 약합니다. 반등 후보로만 보지 말고 손실 확대 위험을 함께 확인하세요."
    return f"{theme} 테마는 현재 중립에 가깝습니다. 종목별 추세와 포트폴리오 비중을 함께 확인하세요."
