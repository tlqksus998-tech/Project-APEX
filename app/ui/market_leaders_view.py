from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import streamlit as st

from app.ui.design_system import section_title
from modules.market.market_leaders import MarketLeaderItem, MarketLeadersResult
from modules.utils import format_currency


LEADER_SECTIONS = [
    ("kospi_market_cap", "KOSPI 시가총액"),
    ("kospi_trading_value", "KOSPI 거래대금"),
    ("nasdaq_market_cap", "NASDAQ 시가총액"),
    ("nasdaq_trading_value", "NASDAQ 거래대금"),
]


def render_market_leaders(result: MarketLeadersResult) -> None:
    """Render market leaders dashboard."""

    section_title("시장 주도주", "KOSPI와 NASDAQ 주요 종목을 기준별로 확인합니다. NASDAQ은 MVP 대표 대형주 유니버스 기준입니다.")
    if result.error_message:
        st.warning(result.error_message)
    st.caption(f"데이터 기준: {result.updated_at}")

    tabs = st.tabs([label for _, label in LEADER_SECTIONS])
    groups = [
        result.kospi_market_cap_top10,
        result.kospi_trading_value_top10,
        result.nasdaq_market_cap_top10,
        result.nasdaq_trading_value_top10,
    ]
    for tab, (section_id, _), items in zip(tabs, LEADER_SECTIONS, groups, strict=True):
        with tab:
            render_market_leader_table(items)
            render_market_leader_cards(items, section_id=section_id)


def render_market_leader_table(items: list[MarketLeaderItem]) -> None:
    """Render market leader rows as a table."""

    if not items:
        st.info("표시할 시장 주도주 데이터가 없습니다.")
        return
    frame = pd.DataFrame([asdict(item) for item in items])
    display = frame.copy()
    display["price"] = display["price"].map(format_currency)
    display["market_cap"] = display["market_cap"].map(format_currency)
    display["trading_value"] = display["trading_value"].map(format_currency)
    display["change_pct"] = display["change_pct"].map(lambda value: f"{value:.2f}%")
    st.dataframe(
        display[["rank", "name", "ticker", "price", "change_pct", "market_cap", "trading_value", "updated_at", "source"]],
        width="stretch",
        hide_index=True,
    )


def render_market_leader_cards(items: list[MarketLeaderItem], section_id: str) -> None:
    """Render compact market leader cards with analysis handoff buttons."""

    with st.expander("카드로 보기", expanded=False):
        for index, item in enumerate(items):
            render_market_leader_card(item, section_id=section_id, index=index)


def render_market_leader_card(item: MarketLeaderItem, section_id: str, index: int) -> None:
    """Render one market leader card."""

    with st.container(border=True):
        cols = st.columns([0.12, 0.48, 0.22, 0.18], vertical_alignment="center")
        cols[0].markdown(f"### {item.rank}")
        cols[1].markdown(f"**{item.name}**")
        cols[1].caption(f"{item.ticker} · {item.market} · {item.source}")
        cols[2].metric("현재가", format_currency(item.price), f"{item.change_pct:.2f}%")
        button_key = f"leader_detail_{section_id}_{index}_{item.market}_{item.ticker}"
        if cols[3].button("상세 판단 보기", key=button_key, width="stretch"):
            st.session_state["selected_analysis_ticker"] = item.ticker
            st.session_state["selected_menu"] = "종목 판단 보기"
            st.info("왼쪽 메뉴에서 종목 판단 보기를 선택하면 해당 종목이 우선 표시됩니다.")
