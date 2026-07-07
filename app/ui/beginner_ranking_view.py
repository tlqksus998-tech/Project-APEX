from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.design_system import section_title
from app.ui.mascot import render_mascot_message
from modules.beginner.explain_translator import decision_to_easy_label
from modules.ranking import build_ai_ranking

RANKING_MARKETS = [
    ("KOSPI", "코스피 AI 랭킹 TOP 10"),
    ("KOSDAQ", "코스닥 AI 랭킹 TOP 10"),
    ("NASDAQ", "나스닥 대표종목 AI 랭킹 TOP 10"),
]


def render_beginner_ai_ranking() -> None:
    """Render beginner-friendly AI ranking cards using the shared decision engine."""

    section_title("AI 랭킹", "상세 판단과 같은 엔진으로 계산한 관심 후보를 보여드립니다.")
    st.caption(
        "AI 랭킹과 종목분석은 같은 판단 엔진을 사용합니다. 같은 데이터 기준이라면 AI 점수와 최종 판단이 동일하게 표시됩니다."
    )
    render_mascot_message(
        "점수가 높다고 바로 사라는 뜻은 아닙니다. AI 점수는 종목을 비교하기 위한 참고자료이며, 최종 판단과 오늘의 행동 가이드를 함께 확인해 주세요.",
        role="tofu_pouch",
        tone="info",
    )

    tabs = st.tabs([label for _, label in RANKING_MARKETS])
    for tab, (market, title) in zip(tabs, RANKING_MARKETS, strict=True):
        with tab:
            with st.spinner(f"{title}을 계산하고 있습니다..."):
                ranking = build_ai_ranking(market, limit=10)
            render_ranking_cards(ranking, market_label=market, title=title)


def render_ranking_cards(data: pd.DataFrame, market_label: str, title: str = "") -> None:
    """Render ranking cards from unified AI judgement results."""

    st.markdown(f"### {title or market_label}")
    if data is None or data.empty:
        st.info(
            f"{market_label} 랭킹 데이터를 불러오지 못했습니다.\n\n"
            "가능한 원인:\n"
            "- 미국 주식 데이터 조회가 실패했습니다.\n"
            "- 데이터 기준 시간을 확인하지 못했습니다.\n"
            "- 모든 후보 종목이 데이터 신뢰도 검사에서 제외되었습니다.\n"
            "- 네트워크 또는 yfinance 응답 문제가 있을 수 있습니다.\n\n"
            "잠시 후 다시 시도하거나 개발자 진단 정보를 확인해 주세요."
        )
        render_ranking_diagnostics(data, market_label)
        return

    st.caption(f"표시 종목: {len(data)}개 / 기준: AI 점수 높은 순")
    excluded_count = int(data["excluded_count"].max()) if "excluded_count" in data.columns and not data.empty else 0
    if excluded_count:
        st.caption(f"데이터가 부족하거나 오래되어 랭킹에서 제외된 종목: {excluded_count}개")
    for idx, row in enumerate(data.itertuples(index=False), start=1):
        rank = int(getattr(row, "rank", idx))
        name = str(getattr(row, "name", "종목"))
        ticker = str(getattr(row, "ticker", ""))
        market = str(getattr(row, "market", market_label))
        score = float(getattr(row, "ai_score", 0.0) or 0.0)
        final_signal = str(getattr(row, "final_signal", "WAIT"))
        easy_label = decision_to_easy_label(final_signal)
        one_line = str(getattr(row, "one_line_summary", "") or "데이터를 더 확인해 보세요.")
        data_timestamp = str(getattr(row, "data_timestamp", "") or "-")
        query_timestamp = str(getattr(row, "query_timestamp", "") or "-")
        source = str(getattr(row, "source", "") or "-")
        freshness_status = str(getattr(row, "freshness_status", "") or "unknown")
        readiness_level = str(getattr(row, "readiness_level", "") or "UNKNOWN")
        market_session_label = str(getattr(row, "market_session_label", "") or "확인 필요")
        price_label = str(getattr(row, "price_label", "") or "최근 조회 가격")
        extended_hours_warning = str(getattr(row, "extended_hours_warning", "") or "")
        is_fallback = bool(getattr(row, "is_fallback", False))
        error_message = str(getattr(row, "error_message", "") or "")

        with st.container(border=True):
            st.markdown(f"### {rank}위 {name}")
            st.caption(f"{ticker} / {market}")
            col_score, col_decision = st.columns(2)
            col_score.metric("AI 점수", f"{score:.0f}점")
            col_decision.markdown(f"**최종 판단**  \n{easy_label}")
            st.write(f"**한 줄 결론:** {one_line}")
            st.caption(
                f"데이터 기준 시간: {data_timestamp} / 최근 조회: {query_timestamp} / "
                f"상태: {readiness_level}({freshness_status}) / 세션: {market_session_label} / 가격: {price_label} / 출처: {source}"
            )
            if readiness_level == "CAUTION":
                st.caption("주의: 최근 조회 기준 데이터이며, 정규장 실시간 시세가 아닐 수 있습니다.")
            if extended_hours_warning:
                st.warning(extended_hours_warning)
            if is_fallback:
                st.warning(f"일부 데이터는 대체값을 사용했습니다. {error_message}".strip())

            button_key = f"ai_rank_detail_{market_label}_{idx}_{ticker}"
            if st.button("상세 판단 보기", key=button_key, width="stretch"):
                st.session_state["selected_analysis_ticker"] = ticker
                st.session_state["selected_analysis_market"] = market
                st.info("왼쪽 메뉴에서 쉽게 보기 > 종목분석을 선택하면 같은 판단 엔진으로 상세 결과를 확인할 수 있습니다.")


def render_ranking_diagnostics(data: pd.DataFrame | None, market_label: str) -> None:
    """Render compact diagnostics for ranking load failures."""

    with st.expander(f"{market_label} 랭킹 진단", expanded=False):
        if data is None:
            st.write("랭킹 결과 객체가 없습니다.")
            return
        st.write(f"반환 행 수: {len(data)}")
        st.write(f"컬럼: {', '.join(str(column) for column in data.columns)}")
        if "excluded_count" in data.columns and not data.empty:
            st.write(f"제외 종목 수: {int(data['excluded_count'].max())}")
        elif "excluded_count" in data.columns:
            st.write("제외 종목 수: 결과 없음")
        st.write("READY/CAUTION 데이터는 표시 대상이고, BLOCKED/fallback/sample 데이터는 제외됩니다.")
