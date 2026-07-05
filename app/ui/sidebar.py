from __future__ import annotations

import streamlit as st

from modules.market.master_search import refresh_master_database


MENU_ITEMS = ["Home", "Portfolio", "Market", "Analysis", "Decision", "Settings"]
K_BEGINNER = "\ucd08\ubcf4\uc790 \ubaa8\ub4dc"
K_ADVANCED = "\uace0\uae09\uc790 \ubaa8\ub4dc"
K_REFRESH = "\uc2dc\uc7a5 \ub370\uc774\ud130 \uac31\uc2e0"


def render_sidebar() -> str:
    """Render the main sidebar navigation and return the selected menu."""

    st.sidebar.title("Project APEX")
    return st.sidebar.radio("Menu", MENU_ITEMS, index=0)


def render_user_mode() -> str:
    """Render beginner/advanced mode selector."""

    st.sidebar.divider()
    selected = st.sidebar.radio("View Mode", [K_BEGINNER, K_ADVANCED], index=0)
    return "advanced" if selected == K_ADVANCED else "beginner"


def render_market_refresh() -> None:
    """Render master market data refresh button."""

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
    st.sidebar.subheader("Market")
    render_market_refresh()
    period = st.sidebar.selectbox("History Period", ["1mo", "3mo", "6mo", "1y"], index=2)
    interval = st.sidebar.selectbox("Interval", ["1d", "1wk"], index=0)
    return period, interval


def render_cash_input() -> float:
    """Render temporary cash input until dedicated portfolio cash tracking exists."""

    st.sidebar.divider()
    st.sidebar.subheader("Portfolio")
    return float(st.sidebar.number_input("Cash Amount", min_value=0.0, value=0.0, step=1000.0))
