from __future__ import annotations

import streamlit as st

from modules.portfolio_engine.models import PortfolioEngineSnapshot
from modules.utils import format_currency, format_percent

K_TITLE = "Investment OS Dashboard"
K_RECOMMENDED_CASH = "10~20%"


def render_investment_os_header(snapshot: PortfolioEngineSnapshot) -> None:
    """Render Investment Operating System header metrics."""

    st.subheader(K_TITLE)
    row1 = st.columns(5)
    row1[0].metric("\ucd1d\uc790\uc0b0", format_currency(snapshot.total_assets_krw))
    row1[1].metric("\ucd1d\ud22c\uc790\uae08", format_currency(snapshot.total_invested_krw))
    row1[2].metric("\ucd1d\ud604\uae08", format_currency(snapshot.total_cash_krw))
    row1[3].metric("\ud604\uae08\ube44\uc911", format_percent(snapshot.cash_ratio))
    row1[4].metric("\ucd94\uac00\ud22c\uc790\uac00\ub2a5\uae08\uc561", format_currency(snapshot.investable_cash_krw))

    row2 = st.columns(6)
    row2[0].metric("KRW Cash", format_currency(snapshot.krw_cash))
    row2[1].metric("USD Cash", f"${snapshot.usd_cash:,.2f}")
    row2[2].metric("KRW \ube44\uc911", format_percent(snapshot.krw_weight))
    row2[3].metric("USD \ube44\uc911", format_percent(snapshot.usd_weight))
    row2[4].metric("\ud55c\uad6d \ub178\ucd9c", format_percent(snapshot.korea_exposure))
    row2[5].metric("\ubbf8\uad6d \ub178\ucd9c", format_percent(snapshot.us_exposure))

    row3 = st.columns(2)
    row3[0].metric("Recommended Cash Ratio", K_RECOMMENDED_CASH)
    row3[1].metric("USD/KRW", f"{snapshot.usdkrw:,.0f}")
