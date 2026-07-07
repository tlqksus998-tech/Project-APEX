from __future__ import annotations

import streamlit as st

from app.ui.design_system import section_title
from app.ui.mascot import get_mascot_for_signal, render_mascot_message
from app.ui.portfolio_view import SearchResult, build_search_results
from app.ui.stock_analysis_view import analyze_selected_stock
from app.ui.visual_components import render_meaning_row, render_position_bar, render_score_bar
from modules.beginner.explain_translator import (
    build_beginner_reasons,
    build_beginner_warnings,
    decision_to_easy_label,
    describe_interest,
    describe_price_position,
    describe_risk,
    describe_trend,
    optional_float,
)


def render_beginner_stock_analysis(default_query: str = "") -> None:
    """Render simple stock analysis for beginner users."""

    section_title("종목분석", "궁금한 종목을 쉽고 빠르게 이해하는 화면입니다.")
    st.caption("어려운 지표 이름보다 지금 어떤 느낌인지 먼저 보여드릴게요.")
    query = st.text_input("종목명 또는 티커", value=default_query, placeholder="예: SK하이닉스, 삼성전자, NVDA, MU", key="beginner_stock_query")
    results = build_search_results(query)
    if query and not results:
        st.warning("검색 결과가 없어요. 종목명이나 티커를 다시 확인해 주세요.")
        return
    if not results:
        st.info("종목을 검색하면 3초 요약 카드가 나옵니다.")
        return

    selected = select_beginner_result(results)
    with st.spinner("종목을 쉽게 풀어보는 중이에요..."):
        detail = analyze_selected_stock(selected)
    render_beginner_stock_result(selected, detail)


def select_beginner_result(results: list[SearchResult]) -> SearchResult:
    """Select one beginner search result."""

    labels = [result.label for result in results]
    selected_label = st.selectbox("검색 결과", labels, key="beginner_stock_result")
    return results[labels.index(selected_label)]


def render_beginner_stock_result(selected: SearchResult, detail: dict[str, object]) -> None:
    """Render beginner stock analysis result."""

    analysis = detail["analysis"]
    decision = detail["decision"]
    unified = detail.get("unified")
    if decision is None or analysis is None:
        st.warning("실제 시장 데이터를 충분히 확인하지 못해 AI 점수와 판단을 제공하지 않습니다. 데이터를 다시 조회한 뒤 확인해 주세요.")
        if unified is not None:
            st.caption(
                f"데이터 기준: {getattr(unified, 'data_timestamp', '확인 불가')} / "
                f"최근 조회: {getattr(unified, 'query_timestamp', '확인 불가')} / "
                f"상태: {getattr(unified, 'freshness_status', 'unknown')}"
            )
        return
    decision_dict = decision.__dict__ | {"decision": decision.decision.value, "final_decision": decision.final_decision}
    analysis_dict = analysis.__dict__
    score = optional_float(decision_dict.get("final_score")) or 45.0
    easy_label = decision_to_easy_label(decision_dict.get("final_decision") or decision_dict.get("decision"))
    mascot = get_mascot_for_signal(decision_dict.get("final_decision") or decision_dict.get("decision"))
    week52 = optional_float(analysis_dict.get("week52_position"))
    rsi = optional_float(analysis_dict.get("rsi_14"))

    if unified is not None:
        st.caption(
            f"데이터 기준: {getattr(unified, 'data_timestamp', '확인 불가')} / "
            f"최근 조회: {getattr(unified, 'query_timestamp', '확인 불가')} / "
            f"상태: {getattr(unified, 'readiness_level', 'UNKNOWN')} / "
            f"가격 기준: {getattr(unified, 'price_label', '최근 조회 가격')}"
        )
        extended_warning = getattr(unified, "extended_hours_warning", "")
        if extended_warning:
            st.warning(str(extended_warning))

    with st.container(border=True):
        st.markdown(f"### {selected.name}")
        st.caption(selected.ticker)
        col1, col2 = st.columns([0.55, 0.45])
        col1.markdown(f"#### {easy_label}")
        col2.metric("AI 점수", f"{score:.0f}점")
        st.write(build_one_line(analysis_dict, decision_dict))
        st.warning(describe_risk(decision_dict.get("final_decision"), rsi))

    render_mascot_message(mascot["message"], role=mascot["role"], tone=mascot["tone"])
    render_score_bar("AI 점수", score, left="조심", right="좋음")
    render_position_bar("가격 위치", week52, left="싸요", right="비싸요")

    cols = st.columns(2)
    with cols[0]:
        render_meaning_row("최근 흐름", describe_trend(analysis_dict.get("trend_status"), analysis_dict.get("macd_status")))
        render_meaning_row("관심도", describe_interest(analysis_dict.get("volume_status")))
    with cols[1]:
        render_meaning_row("위험도", describe_risk(decision_dict.get("final_decision"), rsi))
        render_meaning_row("가격 느낌", describe_price_position(week52))

    reason_col, warning_col = st.columns(2)
    with reason_col:
        st.markdown("#### 왜 좋게 보나요?")
        for index, reason in enumerate(build_beginner_reasons(analysis_dict, decision_dict), start=1):
            st.write(f"{index}. {reason}")
    with warning_col:
        st.markdown("#### 주의할 점도 있어요")
        for index, warning in enumerate(build_beginner_warnings(analysis_dict, decision_dict), start=1):
            st.write(f"{index}. {warning}")

    with st.expander("어려운 지표는 이렇게 바꿔 읽어요", expanded=False):
        st.write("RSI가 낮거나 중립이면: 아직 너무 많이 오른 상태는 아니에요.")
        st.write("RSI가 높으면: 조금 뜨거워졌어요. 급하게 사기보다는 조심해요.")
        st.write("거래량이 늘면: 평소보다 관심이 커졌어요.")
        st.write("MACD가 좋으면: 오르는 흐름이 시작되고 있어요.")


def build_one_line(analysis: dict[str, object], decision: dict[str, object]) -> str:
    """Build one simple sentence for beginner summary."""

    interest = describe_interest(analysis.get("volume_status"))
    price = describe_price_position(optional_float(analysis.get("week52_position")))
    if "더 많이" in interest:
        return f"{interest}. {price}."
    score = optional_float(decision.get("final_score")) or 45.0
    if score >= 70:
        return f"흐름이 나쁘지 않고, {price}."
    return "지금은 결론보다 흐름을 더 확인하는 게 좋아요."
