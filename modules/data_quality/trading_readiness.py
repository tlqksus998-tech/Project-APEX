from __future__ import annotations

from datetime import datetime

from modules.data_quality.data_quality_models import MarketDataFreshness, TradingReadinessResult
from modules.data_quality.freshness import is_decision_source_allowed
from modules.data_quality.market_clock import extended_hours_warning, is_extended_hours_session, is_korean_market, market_session_label


def build_trading_readiness(
    ticker: str,
    name: str,
    market: str,
    source: str,
    success: bool,
    freshness: MarketDataFreshness,
    ai_score: float | None = None,
) -> TradingReadinessResult:
    """Build the practical readiness checklist before showing AI judgement."""

    checklist = build_final_trading_checklist(market)
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    sample_data_ok = is_decision_source_allowed(source, success)
    if not sample_data_ok:
        blocking_reasons.append("실제 시장 데이터가 아니거나 데이터 조회에 실패했습니다.")
    if freshness.freshness_status in {"unknown", "invalid"}:
        blocking_reasons.append("데이터 기준 시간을 확인할 수 없습니다.")
    if freshness.is_stale:
        blocking_reasons.append("데이터가 오래되어 판단에 사용할 수 없습니다.")

    session = freshness.market_session or "unknown"
    extended = (not is_korean_market(market)) and is_extended_hours_session(session)
    ext_warning = extended_hours_warning(session) if extended else ""
    if ext_warning:
        warnings.append(ext_warning)

    if freshness.readiness_level == "READY" and extended:
        level = "CAUTION"
    elif blocking_reasons:
        level = "BLOCKED" if freshness.freshness_status != "unknown" else "UNKNOWN"
    else:
        level = freshness.readiness_level

    if level == "CAUTION" and not warnings:
        warnings.append("데이터가 일부 지연되었거나 정규장 데이터가 아닐 수 있습니다. AI 판단은 보수적으로 확인해 주세요.")

    price_label = build_price_label(market, session, level)
    final_message = build_final_message(level)
    return TradingReadinessResult(
        ticker=ticker,
        name=name,
        market=market,
        is_ready_for_reference=level in {"READY", "CAUTION"},
        readiness_level=level,
        checklist=checklist,
        blocking_reasons=blocking_reasons,
        warning_messages=warnings,
        data_timestamp=freshness.data_timestamp,
        query_timestamp=freshness.query_timestamp,
        data_age_minutes=freshness.age_minutes,
        price_status="reference_price" if level in {"READY", "CAUTION"} else "unavailable",
        price_label=price_label,
        freshness_status=freshness.freshness_status,
        score_consistency_status="common_engine" if ai_score is not None else "not_scored",
        sample_data_status="blocked" if not sample_data_ok else "clean",
        market_session=session,
        market_session_label=market_session_label(session),
        is_extended_hours=extended,
        extended_hours_type=session if extended else "",
        extended_hours_warning=ext_warning,
        requires_extended_hours_confirmation=extended,
        final_message=final_message,
    )


def build_price_label(market: str, session: str, readiness_level: str) -> str:
    """Return a clear price label that avoids realtime claims."""

    if readiness_level in {"BLOCKED", "UNKNOWN"}:
        return "가격 기준 확인 불가"
    if is_korean_market(market):
        if session == "regular":
            return "최근 조회 가격"
        if session == "closed":
            return "최근 거래일 기준 가격"
        return "최근 가격"
    if session == "pre_market":
        return "프리장 기준 최근 가격"
    if session == "after_market":
        return "애프터장 기준 최근 가격"
    if session == "regular":
        return "최근 조회 가격"
    return "최근 거래일 기준 가격"


def build_final_message(level: str) -> str:
    """Return the final readiness message."""

    if level == "READY":
        return "실전 참고 가능: 최근 조회 기준 데이터로 AI 판단을 제공합니다. 최종 매매 전 현재가와 뉴스를 확인해 주세요."
    if level == "CAUTION":
        return "주의 필요: 데이터가 일부 지연되었거나 정규장 데이터가 아닐 수 있습니다. AI 판단은 참고만 해 주세요."
    if level == "BLOCKED":
        return "판단 제한: 현재 데이터 상태로는 AI 판단을 제공하지 않습니다. 데이터를 다시 조회해 주세요."
    return "확인 필요: 데이터 상태를 판단할 수 없습니다. 직접 확인 후 사용해 주세요."


def build_final_trading_checklist(market: str) -> list[str]:
    """Return final checklist text for beginner users."""

    items = [
        "증권사 앱의 현재가가 APEX의 최근 가격과 크게 다르지 않은지 확인했습니다.",
        "오늘 갑작스러운 뉴스나 공시가 없는지 확인했습니다.",
        "거래량과 호가가 급격히 흔들리고 있지 않은지 확인했습니다.",
        "내 현금비중과 종목 비중을 확인했습니다.",
        "손절 기준 또는 비중축소 기준을 미리 정했습니다.",
        "이 판단은 자동매매 지시가 아니라 참고자료임을 이해했습니다.",
    ]
    if not is_korean_market(market):
        items.extend(
            [
                "현재 가격이 프리장 또는 애프터장 가격인지 확인했습니다.",
                "프리장/애프터장은 정규장보다 거래량이 적고 변동성이 클 수 있음을 이해했습니다.",
                "정규장 시작 후 가격이 달라질 수 있음을 확인했습니다.",
            ]
        )
    return items


def format_minutes(value: float | None) -> str:
    """Format age minutes for UI display."""

    if value is None:
        return "확인 불가"
    return f"{value:.0f}분"
