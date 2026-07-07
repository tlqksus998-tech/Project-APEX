from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.design_system import badge, section_title
from app.ui.portfolio_view import SearchResult, build_search_results
from modules.ai_judgement import build_ai_judgement_summary
from modules.analysis.analysis_engine import analyze_ohlcv
from modules.config import get_config
from modules.decision.decision_engine import decide_one
from modules.market.market_models import MarketDataRequest
from modules.market.ohlcv_provider import get_ohlcv
from modules.market.price_provider import get_current_price
from modules.portfolio.session_state import add_holding
from modules.utils import format_currency


def render_stock_analysis_view(default_query: str = "") -> None:
    """Render standalone stock detail analysis without requiring portfolio ownership."""

    section_title("종목 판단 보기", "포트폴리오에 추가하지 않아도 종목의 현재 흐름과 APEX 판단을 확인할 수 있습니다.")
    query = st.text_input("종목 검색", value=default_query, placeholder="삼성전자, SK하이닉스, NVDA, MU, TIGER 미국S&P500", key="stock_analysis_query")
    results = build_search_results(query)

    if query and not results:
        st.warning("검색 결과가 없습니다. 종목명이나 티커를 다시 확인하세요.")
        return
    if not results:
        st.info("종목명을 검색하면 상세 판단 카드가 표시됩니다.")
        return

    selected = select_search_result(results)
    if selected is None:
        return

    with st.spinner("선택 종목을 분석하는 중입니다..."):
        detail = analyze_selected_stock(selected)

    render_stock_detail(selected, detail)
    render_add_to_portfolio_form(selected)


def select_search_result(results: list[SearchResult]) -> SearchResult | None:
    """Render a result selector and return the selected search result."""

    st.caption(f"검색 결과: {len(results)}개")
    labels = [result.label for result in results]
    default_ticker = str(st.session_state.get("selected_analysis_ticker", "")).upper()
    default_index = 0
    if default_ticker:
        for index, result in enumerate(results):
            if result.ticker.upper() == default_ticker:
                default_index = index
                break
    selected_label = st.selectbox("검색 결과 선택", labels, index=default_index, key="stock_analysis_result")
    return results[labels.index(selected_label)] if selected_label in labels else None


def analyze_selected_stock(selected: SearchResult) -> dict[str, object]:
    """Run price, OHLCV, analysis, decision, and AI summary for one selected stock."""

    config = get_config()
    price = get_current_price(selected.ticker, config, market_hint=selected.market)
    ohlcv = get_ohlcv(MarketDataRequest(ticker=selected.ticker, period="6mo", interval="1d", market_hint=selected.market), config)
    analysis = analyze_ohlcv(selected.ticker, ohlcv.data)
    decision = decide_one(analysis.__dict__)
    summary = build_ai_judgement_summary(
        selected.name,
        selected.ticker,
        analysis.__dict__,
        decision.__dict__ | {"decision": decision.decision.value, "final_decision": decision.final_decision, "stock_signal": decision.stock_signal},
    )
    return {"price": price, "ohlcv": ohlcv, "analysis": analysis, "decision": decision, "summary": summary}


def render_stock_detail(selected: SearchResult, detail: dict[str, object]) -> None:
    """Render a selected stock detail analysis panel."""

    price = detail["price"]
    analysis = detail["analysis"]
    decision = detail["decision"]
    summary = detail["summary"]

    st.markdown(f"### {selected.name} ({selected.ticker})")
    cols = st.columns(4)
    cols[0].metric("시장", selected.market)
    cols[1].metric("거래통화", selected.trading_currency)
    cols[2].metric("현재가", format_currency(price.current_price))
    cols[3].markdown(badge(decision.final_decision), unsafe_allow_html=True)

    cols = st.columns(4)
    cols[0].metric("RSI", format_optional(analysis.rsi_14))
    cols[1].metric("MACD", analysis.macd_status)
    cols[2].metric("추세", analysis.trend_status)
    cols[3].metric("52주 위치", f"{analysis.week52_position:.1f}" if analysis.week52_position is not None else "데이터 부족")

    with st.container(border=True):
        st.markdown(f"#### {summary.title}")
        st.write(summary.summary_text)
        metric_cols = st.columns(3)
        metric_cols[0].metric("현재 신호", summary.signal)
        metric_cols[1].metric("APEX Score", f"{summary.score:.0f}")
        metric_cols[2].metric("신뢰도", f"{summary.confidence:.0f}%")
        st.markdown("**긍정 요인**")
        for item in summary.positives:
            st.write(f"- {item}")
        st.markdown("**주의 요인**")
        for item in summary.risks:
            st.write(f"- {item}")
        st.markdown("**대응 전략**")
        st.write(summary.strategy)
        st.markdown("**추천 행동**")
        st.info(summary.action)

    if not price.success or not detail["ohlcv"].success:
        st.caption("일부 데이터는 조회 실패로 샘플 또는 fallback 값을 사용했습니다.")


def render_add_to_portfolio_form(selected: SearchResult) -> None:
    """Render optional add-to-portfolio controls for the selected stock."""

    with st.expander("포트폴리오에 추가", expanded=False):
        st.caption(f"{selected.name} / {selected.ticker} / {selected.trading_currency}")
        col_qty, col_price = st.columns(2)
        quantity = col_qty.number_input("수량", min_value=0.0, value=1.0, step=1.0, key="detail_add_quantity")
        avg_price = col_price.number_input(f"평균단가({selected.trading_currency})", min_value=0.0, value=0.0, step=100.0 if selected.trading_currency == "KRW" else 1.0, key="detail_add_avg_price")
        memo = st.text_input("메모 optional", key="detail_add_memo")
        if st.button("포트폴리오에 추가", type="primary", width="stretch", key="detail_add_button"):
            success, message = add_holding(selected.name, selected.ticker, quantity, avg_price)
            if success:
                st.success("포트폴리오에 추가되었습니다. 내 투자 현황에서 전체 포트폴리오 판단을 확인할 수 있습니다.")
                if memo:
                    st.caption(f"메모: {memo}")
            else:
                st.warning(message)
        st.button("관심리스트에 추가", disabled=True, width="stretch", key="detail_watchlist_button", help="관심리스트 기능은 이후 Sprint에서 연결할 예정입니다.")


def format_optional(value: float | None) -> str:
    """Format optional indicator values."""

    if value is None or pd.isna(value):
        return "데이터 부족"
    return f"{float(value):.1f}"
