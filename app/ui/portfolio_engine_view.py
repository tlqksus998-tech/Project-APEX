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
    row1[0].metric("총자산", format_currency(snapshot.total_assets_krw))
    row1[1].metric("총투자금", format_currency(snapshot.total_invested_krw))
    row1[2].metric("총현금", format_currency(snapshot.total_cash_krw))
    row1[3].metric("현금비중", format_percent(snapshot.cash_ratio))
    row1[4].metric("추가투자가능금액", format_currency(snapshot.investable_cash_krw))

    row2 = st.columns(5)
    row2[0].metric("원화 평가금액", format_currency(snapshot.krw_current_value))
    row2[1].metric("달러 평가금액", f"${snapshot.usd_current_value_original:,.2f}")
    row2[2].metric("총 평가금액(KRW)", format_currency(snapshot.total_current_value_krw))
    row2[3].metric("KRW 비중", format_percent(snapshot.krw_weight))
    row2[4].metric("USD 비중", format_percent(snapshot.usd_weight))

    row3 = st.columns(6)
    row3[0].metric("KRW Cash", format_currency(snapshot.krw_cash))
    row3[1].metric("USD Cash", f"${snapshot.usd_cash:,.2f}")
    row3[2].metric("한국 노출", format_percent(snapshot.korea_exposure))
    row3[3].metric("미국 노출", format_percent(snapshot.us_exposure))
    row3[4].metric("Recommended Cash Ratio", K_RECOMMENDED_CASH)
    row3[5].metric("USD/KRW", f"{snapshot.usdkrw:,.0f}")
