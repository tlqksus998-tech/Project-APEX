from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.checklist_view import render_analysis_checklist
from app.ui.design_system import badge, section_title
from app.ui.indicator_visuals import render_rsi_gauge
from app.ui.portfolio_view import SearchResult, build_search_results
from modules.ai_judgement import AIJudgementSummary, build_ai_judgement_summary
from modules.analysis.analysis_engine import analyze_ohlcv
from modules.analysis.checklist import build_analysis_checklist
from modules.config import get_config
from modules.decision.decision_engine import decide_one
from modules.market.market_models import MarketDataRequest, PriceData
from modules.market.ohlcv_provider import get_ohlcv
from modules.market.price_provider import get_current_price
from modules.portfolio.session_state import add_holding
from modules.utils import format_currency


def render_stock_analysis_view(default_query: str = "", beginner_mode: bool = True) -> None:
    """Render standalone stock detail analysis without requiring portfolio ownership."""

    section_title("종목 판단 보기", "궁금한 종목을 검색해 APEX 판단과 쉬운 설명을 확인하는 화면입니다.")
    if beginner_mode:
        st.info("먼저 종목을 검색해 판단을 확인한 뒤, 실제로 보유 중인 종목만 포트폴리오에 추가하세요.")

    query = st.text_input(
        "종목 검색",
        value=default_query,
        placeholder="삼성전자, SK하이닉스, NVDA, MU, TIGER 미국S&P500",
        key="stock_analysis_query",
    )
    results = build_search_results(query)

    if query and not results:
        st.warning("검색 결과가 없습니다. 종목명이나 티커를 다시 확인해 주세요.")
        return
    if not results:
        st.info("종목명을 검색하면 상세 판단 카드가 표시됩니다.")
        return

    selected = select_search_result(results)
    if selected is None:
        return

    with st.spinner("선택한 종목을 분석하는 중입니다..."):
        detail = analyze_selected_stock(selected)

    render_stock_detail(selected, detail, beginner_mode=beginner_mode)
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
    """Run price, OHLCV, analysis, decision, checklist, and AI summary for one selected stock."""

    config = get_config()
    price = get_current_price(selected.ticker, config, market_hint=selected.market)
    ohlcv = get_ohlcv(MarketDataRequest(ticker=selected.ticker, period="6mo", interval="1d", market_hint=selected.market), config)
    analysis = analyze_ohlcv(selected.ticker, ohlcv.data)
    decision = decide_one(analysis.__dict__)
    decision_dict = decision.__dict__ | {
        "decision": decision.decision.value,
        "final_decision": decision.final_decision,
        "stock_signal": decision.stock_signal,
    }
    summary = build_ai_judgement_summary(selected.name, selected.ticker, analysis.__dict__, decision_dict)
    checklist = build_analysis_checklist(analysis.__dict__, decision_dict)
    return {"price": price, "ohlcv": ohlcv, "analysis": analysis, "decision": decision, "summary": summary, "checklist": checklist}


def render_stock_detail(selected: SearchResult, detail: dict[str, object], beginner_mode: bool = True) -> None:
    """Render a selected stock detail analysis panel."""

    price: PriceData = detail["price"]  # type: ignore[assignment]
    analysis = detail["analysis"]
    decision = detail["decision"]
    summary: AIJudgementSummary = detail["summary"]  # type: ignore[assignment]
    checklist = detail["checklist"]

    st.markdown(f"### {selected.name} ({selected.ticker})")
    render_top_decision_card(selected, price, decision, summary)
    render_ai_summary_card(summary)
    render_action_plan(summary)
    render_analysis_checklist(checklist, beginner_mode=beginner_mode)
    render_rsi_gauge(analysis.rsi_14)

    if beginner_mode:
        with st.expander("자세한 지표 보기", expanded=False):
            render_advanced_indicators(selected, price, analysis, decision)
    else:
        render_advanced_indicators(selected, price, analysis, decision)

    if not price.success or not detail["ohlcv"].success:
        st.caption("일부 데이터는 조회 실패로 fallback 값을 사용했습니다. 티커를 확인하거나 잠시 후 다시 시도하세요.")


def render_top_decision_card(selected: SearchResult, price: PriceData, decision: object, summary: AIJudgementSummary) -> None:
    """Render stock identity, current price, final decision, and one-line conclusion."""

    cols = st.columns([0.28, 0.24, 0.20, 0.28])
    cols[0].metric("시장", selected.market)
    cols[1].metric("현재가", format_currency(price.current_price))
    cols[2].markdown(badge(getattr(decision, "final_decision", summary.signal)), unsafe_allow_html=True)
    cols[3].metric("신뢰도", f"{summary.confidence:.0f}%")
    st.info(summary.one_line_conclusion)


def render_ai_summary_card(summary: AIJudgementSummary) -> None:
    """Render expanded rule-based AI judgement summary."""

    with st.container(border=True):
        st.markdown(f"#### {summary.title}")
        metric_cols = st.columns(3)
        metric_cols[0].metric("최종 판단", summary.signal)
        metric_cols[1].metric("APEX Score", f"{summary.score:.0f}")
        metric_cols[2].metric("AI Confidence", f"{summary.confidence:.0f}%")

        st.markdown("**한 줄 결론**")
        st.write(summary.one_line_conclusion)
        st.markdown("**종합 판단**")
        st.write(summary.detailed_summary)

        good_col, caution_col, uncertain_col = st.columns(3)
        with good_col:
            st.markdown("**좋은 점**")
            for item in summary.good_points:
                st.write(f"- {item}")
        with caution_col:
            st.markdown("**주의할 점**")
            for item in summary.caution_points:
                st.write(f"- {item}")
        with uncertain_col:
            st.markdown("**불확실한 점**")
            for item in summary.uncertain_points:
                st.write(f"- {item}")

        st.markdown("**초보자 해석**")
        st.info(summary.beginner_explanation)


def render_action_plan(summary: AIJudgementSummary) -> None:
    """Render practical action plan for today."""

    with st.container(border=True):
        st.markdown("#### 오늘의 대응전략")
        cols = st.columns(4)
        for col, (label, text) in zip(cols, summary.action_plan.items(), strict=False):
            col.markdown(f"**{label}**")
            col.caption(text)


def render_advanced_indicators(selected: SearchResult, price: PriceData, analysis: object, decision: object) -> None:
    """Render advanced technical indicators and score breakdown."""

    st.markdown("#### 상세 지표")
    cols = st.columns(4)
    cols[0].metric("RSI", format_optional(getattr(analysis, "rsi_14", None)))
    cols[1].metric("MACD", str(getattr(analysis, "macd_status", "데이터 부족")))
    cols[2].metric("추세", str(getattr(analysis, "trend_status", "데이터 부족")))
    cols[3].metric("52주 위치", format_optional(getattr(analysis, "week52_position", None)))

    cols = st.columns(4)
    cols[0].metric("거래통화", selected.trading_currency)
    cols[1].metric("데이터 소스", price.source)
    cols[2].metric("Stock Score", format_optional(getattr(decision, "stock_score", None)))
    cols[3].metric("Risk Score", format_optional(getattr(decision, "risk_score", None)))

    with st.expander("Decision Score Breakdown", expanded=False):
        st.write(str(getattr(decision, "advanced_summary", "")))
        warnings = getattr(decision, "warnings", []) or []
        if warnings:
            st.markdown("**Override / Warning**")
            for item in warnings:
                st.write(f"- {item}")


def render_add_to_portfolio_form(selected: SearchResult) -> None:
    """Render optional add-to-portfolio controls for the selected stock."""

    with st.expander("포트폴리오에 추가", expanded=False):
        st.caption(f"{selected.name} / {selected.ticker} / {selected.trading_currency}")
        col_qty, col_price = st.columns(2)
        quantity = col_qty.number_input("수량", min_value=0.0, value=1.0, step=1.0, key="detail_add_quantity")
        avg_price = col_price.number_input(
            f"평균단가({selected.trading_currency})",
            min_value=0.0,
            value=0.0,
            step=100.0 if selected.trading_currency == "KRW" else 1.0,
            key="detail_add_avg_price",
        )
        memo = st.text_input("메모 optional", key="detail_add_memo")
        if st.button("포트폴리오에 추가", type="primary", width="stretch", key="detail_add_button"):
            success, message = add_holding(selected.name, selected.ticker, quantity, avg_price)
            if success:
                st.success("포트폴리오에 추가했습니다. 내 투자 현황에서 전체 포트폴리오 판단을 확인할 수 있습니다.")
                if memo:
                    st.caption(f"메모: {memo}")
            else:
                st.warning(message)
        st.button(
            "관찰리스트에 추가",
            disabled=True,
            width="stretch",
            key="detail_watchlist_button",
            help="관찰리스트 기능은 이후 Sprint에서 연결할 예정입니다.",
        )


def format_optional(value: float | None) -> str:
    """Format optional indicator values."""

    if value is None or pd.isna(value):
        return "데이터 부족"
    return f"{float(value):.1f}"
