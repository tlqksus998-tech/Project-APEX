from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.design_system import badge, section_title

K_TITLE = "오늘의 관심 후보"
K_NOTICE = "오늘의 관심 후보는 바로 매수하라는 의미가 아닙니다. 시장 상황, 종목 흐름, 포트폴리오 비중을 함께 확인하기 위한 검토 대상입니다."
K_EMPTY = "표시할 관심 후보가 아직 없습니다. KRX 종목 DB를 새로고침하거나 잠시 후 다시 확인하세요."


def render_candidate_stocks(candidates: pd.DataFrame) -> None:
    """Render beginner-friendly watchlist candidate cards."""

    st.subheader(K_TITLE)
    st.caption(K_NOTICE)
    if candidates is None or candidates.empty:
        st.info(K_EMPTY)
        return

    visible = candidates.reset_index(drop=True)

    for _, row in visible.iterrows():
        render_candidate_card(row, show_full_reasons=True)


def render_candidate_card(row: pd.Series, show_full_reasons: bool = False) -> None:
    """Render one candidate as an explanatory card."""

    name = str(row.get("name", ""))
    ticker = str(row.get("ticker", ""))
    score = safe_float(row.get("final_score"))
    status = map_watch_status(score)
    reasons = normalize_reasons(row.get("reasons"))
    shown_reasons = reasons[:3] if show_full_reasons else reasons[:2]

    with st.container(border=True):
        col_title, col_status = st.columns([0.68, 0.32], vertical_alignment="center")
        col_title.markdown(f"### {name}")
        col_title.caption(ticker)
        col_status.markdown(badge(status), unsafe_allow_html=True)
        col_status.caption("상태")
        st.write(beginner_explanation(status))
        st.markdown("**핵심 이유**")
        for reason in shown_reasons:
            st.write(f"- {reason}")
        st.warning("주의사항: 관심 후보는 매수 지시가 아닙니다. 현금비중, 손실 위험, 기존 보유 비중을 함께 확인하세요.")


def map_watch_status(score: float) -> str:
    """Map numeric score into beginner-friendly watch status."""

    if score >= 80:
        return "Strong Watch"
    if score >= 65:
        return "Watch"
    if score >= 45:
        return "Wait"
    return "Avoid"


def beginner_explanation(status: str) -> str:
    """Return beginner-friendly explanation for a watch status."""

    explanations = {
        "Strong Watch": "이 종목은 오늘 우선적으로 살펴볼 만합니다. 다만 바로 매수하기보다 분할 접근과 비중을 먼저 확인하세요.",
        "Watch": "관심을 두고 흐름을 확인할 만합니다. 시장 상황과 내 포트폴리오 여유를 함께 보세요.",
        "Wait": "아직은 기다리며 확인하는 편이 좋습니다. 추가 신호가 생기는지 지켜보세요.",
        "Avoid": "현재는 리스크가 상대적으로 커 보입니다. 무리한 진입은 피하는 편이 좋습니다.",
    }
    return explanations.get(status, explanations["Wait"])


def normalize_reasons(value: object) -> list[str]:
    """Normalize reason payload into a short list."""

    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value or "").strip()
    if not text:
        return ["시장 흐름 확인 필요", "포트폴리오 비중 확인 필요"]
    return [part.strip() for part in text.split("|") if part.strip()]


def safe_float(value: object) -> float:
    """Convert a value to float with zero fallback."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def format_reasons(value: object) -> str:
    """Backward-compatible reason formatter."""

    return " | ".join(normalize_reasons(value)[:3])

