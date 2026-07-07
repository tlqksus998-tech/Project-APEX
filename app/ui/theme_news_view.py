from __future__ import annotations

import streamlit as st

from app.ui.design_system import badge
from modules.news.news_models import ThemeNewsResult
from modules.data_freshness import format_timestamp


def render_theme_news(result: ThemeNewsResult) -> None:
    """Render theme news cards with explicit fallback/demo labels."""

    st.markdown("#### 선택 테마 주요 뉴스")
    if result.is_fallback:
        st.markdown(badge("Demo"), unsafe_allow_html=True)
        st.caption(result.error_message)
    st.caption(f"뉴스 데이터 기준: {format_timestamp(result.updated_at)} / 출처: {result.source}")
    for item in result.items:
        with st.container(border=True):
            st.markdown(f"**{item.title}**")
            st.caption(f"{item.source} · {format_timestamp(item.published_at)} · {item.impact_level} · {item.sentiment_label}")
            st.write(item.summary)
            if item.related_tickers:
                st.caption("관련 종목: " + ", ".join(item.related_tickers))
            if item.url:
                st.link_button("원문 보기", item.url)
            if item.is_fallback:
                st.caption("Demo/Sample 뉴스입니다. 실제 뉴스처럼 해석하지 마세요.")
    st.info("뉴스는 투자 참고자료이며 매수 추천이나 수익 보장을 의미하지 않습니다.")
