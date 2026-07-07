from __future__ import annotations

import streamlit as st

from modules.config.version import APP_NAME, APP_VERSION, BUILD_DATE, BUILD_NAME
from modules.data_providers.fx_provider import get_usdkrw_rate
from modules.market.master_search import refresh_krx_master_database, refresh_master_database
from modules.portfolio_engine import CashPosition

EASY_MODE = "쉽게 보기"
DEVELOPER_MODE = "개발자 모드"

EASY_MENU_ITEMS = ["종목분석", "AI 랭킹"]
DEVELOPER_MENU_ITEMS = ["내 투자 현황", "종목 판단 보기", "시장 주도주", "테마 레이더", "포트폴리오 관리", "시장 브리핑", "설정"]

EASY_ROUTE_PREFIX = "쉽게 보기 · "
DEVELOPER_ROUTE_PREFIX = "개발자 모드 · "
MENU_ITEMS = [f"{EASY_ROUTE_PREFIX}{item}" for item in EASY_MENU_ITEMS] + [f"{DEVELOPER_ROUTE_PREFIX}{item}" for item in DEVELOPER_MENU_ITEMS]

K_BEGINNER = "초보자 모드"
K_ADVANCED = "고급자 모드"
K_REFRESH = "시장 데이터 갱신"
K_KRX_REFRESH = "KRX 종목 DB 새로고침"


def render_sidebar() -> str:
    """Render two-track navigation and return the selected route key."""

    st.sidebar.title("Project APEX")
    st.sidebar.caption("AI Portfolio Expert")
    track = st.sidebar.radio("화면 선택", [EASY_MODE, DEVELOPER_MODE], index=0, key="apex_track")
    if track == EASY_MODE:
        selected = st.sidebar.radio("쉽게 보기", EASY_MENU_ITEMS, index=0, key="easy_menu")
        route = f"{EASY_ROUTE_PREFIX}{selected}"
    else:
        selected = st.sidebar.radio("개발자 모드", DEVELOPER_MENU_ITEMS, index=0, key="developer_menu")
        route = f"{DEVELOPER_ROUTE_PREFIX}{selected}"
    st.session_state["selected_menu"] = route
    return route


def render_user_mode() -> str:
    """Render beginner/advanced mode selector."""

    st.sidebar.divider()
    if st.session_state.get("apex_track", EASY_MODE) == EASY_MODE:
        st.sidebar.caption("쉽게 보기에서는 어려운 지표보다 쉬운 설명을 먼저 보여줍니다.")
        return "beginner"
    selected = st.sidebar.radio("View Mode", [K_BEGINNER, K_ADVANCED], index=1)
    return "advanced" if selected == K_ADVANCED else "beginner"


def render_market_refresh() -> None:
    """Render master market data refresh button."""

    if st.sidebar.button(K_KRX_REFRESH, width="stretch"):
        with st.sidebar.spinner("Updating KRX data..."):
            success, message = refresh_krx_master_database()
        if success:
            st.sidebar.success(message)
        else:
            st.sidebar.warning(message)
    if st.sidebar.button(K_REFRESH, width="stretch"):
        with st.sidebar.spinner("Updating market data..."):
            success, message = refresh_master_database()
        if success:
            st.sidebar.success(message)
        else:
            st.sidebar.warning(message)


def render_market_controls() -> tuple[str, str]:
    """Render market data controls and return period and interval."""

    st.sidebar.divider()
    st.sidebar.subheader("Market Controls")
    render_market_refresh()
    period = st.sidebar.selectbox("History Period", ["1mo", "3mo", "6mo", "1y"], index=2)
    interval = st.sidebar.selectbox("Interval", ["1d", "1wk"], index=0)
    return period, interval


def render_cash_inputs() -> CashPosition:
    """Render KRW/USD cash and FX inputs."""

    st.sidebar.divider()
    st.sidebar.subheader("Cash / Currency")
    krw_cash = float(
        st.sidebar.number_input(
            "KRW Cash",
            min_value=0.0,
            value=float(st.session_state.get("krw_cash", 0.0)),
            step=10000.0,
            key="sidebar_krw_cash",
        )
    )
    usd_cash = float(
        st.sidebar.number_input(
            "USD Cash",
            min_value=0.0,
            value=float(st.session_state.get("usd_cash", 0.0)),
            step=100.0,
            key="sidebar_usd_cash",
        )
    )
    st.session_state["krw_cash"] = krw_cash
    st.session_state["usd_cash"] = usd_cash
    if "fx_rate" not in st.session_state:
        st.session_state["fx_rate"] = 1380.0
    if st.sidebar.button("환율 최신화", width="stretch", key="refresh_fx_rate", type="primary"):
        result = get_usdkrw_rate(float(st.session_state.get("fx_rate", 1380.0)))
        st.session_state["fx_rate"] = result.rate
        st.session_state["fx_updated_at"] = result.updated_at
        st.session_state["fx_source"] = result.source
        if result.success:
            st.sidebar.success(f"환율: {result.rate:,.1f}원")
        else:
            st.sidebar.warning(result.error_message)
    usdkrw = float(st.sidebar.number_input("USD/KRW", min_value=0.0, value=float(st.session_state.get("fx_rate", 1380.0)), step=10.0))
    st.session_state["fx_rate"] = usdkrw
    return CashPosition(krw_cash=krw_cash, usd_cash=usd_cash, usdkrw=usdkrw)


def render_cash_input() -> float:
    """Backward-compatible total cash input helper."""

    return render_cash_inputs().total_cash_krw


def render_version_footer() -> None:
    """Render version footer in the sidebar."""

    st.sidebar.divider()
    st.sidebar.caption(f"{APP_NAME} {APP_VERSION}")
    st.sidebar.caption(BUILD_NAME)
    st.sidebar.caption(f"Last Updated: {BUILD_DATE}")
