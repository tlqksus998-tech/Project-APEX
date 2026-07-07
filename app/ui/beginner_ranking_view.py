from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.design_system import section_title
from app.ui.mascot import render_mascot_message
from modules.beginner.explain_translator import decision_to_easy_label
from modules.screening import screen_today_candidates

NASDAQ_SAMPLE = pd.DataFrame(
    [
        {"name": "NVIDIA", "ticker": "NVDA", "market": "NASDAQ", "final_score": 90, "decision": "BUY", "reasons": ["AI 반도체 관심이 커요", "최근 흐름이 좋아요"]},
        {"name": "Microsoft", "ticker": "MSFT", "market": "NASDAQ", "final_score": 84, "decision": "HOLD", "reasons": ["큰 회사라 안정감이 있어요", "흐름을 더 확인해요"]},
        {"name": "Apple", "ticker": "AAPL", "market": "NASDAQ", "final_score": 78, "decision": "HOLD", "reasons": ["관심이 꾸준해요", "가격 부담을 확인해요"]},
    ]
)


def render_beginner_ai_ranking() -> None:
    """Render beginner-friendly AI ranking cards."""

    section_title("AI 랭킹", "오늘 살펴볼 만한 종목을 쉽게 정리했습니다.")
    st.caption("이 화면은 매수 지시가 아니라 관심 종목을 빠르게 고르는 참고자료입니다.")
    render_mascot_message(
        "순위는 바로 사라는 뜻이 아니에요. 먼저 관심 후보를 고르고, 자세히 보기에서 흐름과 주의할 점을 함께 확인해 주세요.",
        role="tofu_pouch",
        tone="info",
    )
    tab_kospi, tab_nasdaq = st.tabs(["코스피", "나스닥"])
    with tab_kospi:
        kospi = screen_today_candidates(limit=5)
        render_ranking_cards(kospi, market_label="코스피")
    with tab_nasdaq:
        render_ranking_cards(NASDAQ_SAMPLE, market_label="나스닥")


def render_ranking_cards(data: pd.DataFrame, market_label: str) -> None:
    """Render ranking cards from a candidate frame."""

    if data is None or data.empty:
        st.info(f"{market_label} 랭킹을 아직 만들 수 없어요. 시장 데이터를 갱신한 뒤 다시 확인해 주세요.")
        return
    for index, row in enumerate(data.head(5).itertuples(index=False), start=1):
        name = str(getattr(row, "name", "종목"))
        ticker = str(getattr(row, "ticker", ""))
        score = float(getattr(row, "final_score", 0.0) or 0.0)
        decision = decision_to_easy_label(getattr(row, "decision", "HOLD"))
        reasons = getattr(row, "reasons", []) or []
        with st.container(border=True):
            st.markdown(f"### {index}위 {name}")
            st.caption(ticker)
            col_score, col_decision = st.columns(2)
            col_score.metric("AI 점수", f"{score:.0f}점")
            col_decision.markdown(f"**AI 판단**  \n{decision}")
            st.write("최근 흐름: 살펴볼 만한 흐름")
            st.write("가격 느낌: 아직 너무 비싸 보이지는 않아요")
            st.warning("주의: 단기 흔들림 가능")
            if reasons:
                st.caption("이유: " + " / ".join(str(item) for item in reasons[:2]))
            button_key = f"beginner_rank_detail_{market_label}_{index}_{ticker}"
            if st.button("상세 판단 보기", key=button_key, width="stretch"):
                st.session_state["selected_analysis_ticker"] = ticker
                st.info("왼쪽 메뉴에서 쉽게 보기 > 종목분석을 선택하면 이 종목의 상세 판단을 확인할 수 있습니다.")
