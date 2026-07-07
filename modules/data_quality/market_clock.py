from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")
NY = ZoneInfo("America/New_York")


def normalize_market_datetime(value: datetime | None, market: str) -> datetime | None:
    """Return a timezone-aware timestamp for the given market."""

    if value is None:
        return None
    zone = market_timezone(market)
    return value.astimezone(zone) if value.tzinfo else value.replace(tzinfo=zone)


def market_timezone(market: str) -> ZoneInfo:
    """Return a simple market timezone."""

    return KST if is_korean_market(market) else NY


def is_korean_market(market: str) -> bool:
    """Return whether market label is Korean."""

    value = str(market or "").upper()
    return any(token in value for token in ["KR", "KOSPI", "KOSDAQ", "KONEX", "KRX"])


def get_market_session(market: str, current: datetime | None = None) -> tuple[str, bool]:
    """Return simple market session and trade-time flag."""

    zone = market_timezone(market)
    now = current.astimezone(zone) if current and current.tzinfo else (current.replace(tzinfo=zone) if current else datetime.now(zone))
    if now.weekday() >= 5:
        return "closed", False

    if is_korean_market(market):
        regular_start = time(9, 0)
        regular_end = time(15, 30)
        if regular_start <= now.time() <= regular_end:
            return "regular", True
        return "closed", False

    regular_start = time(9, 30)
    regular_end = time(16, 0)
    if regular_start <= now.time() <= regular_end:
        return "regular", True
    if time(4, 0) <= now.time() < regular_start:
        return "pre_market", False
    if regular_end < now.time() <= time(20, 0):
        return "after_market", False
    return "closed", False


def market_session_label(session: str) -> str:
    """Return Korean label for a market session."""

    return {
        "pre_market": "프리장",
        "regular": "정규장",
        "after_market": "애프터장",
        "closed": "장외/휴장 가능",
        "unknown": "확인 필요",
    }.get(str(session or "unknown"), "확인 필요")


def is_extended_hours_session(session: str) -> bool:
    """Return whether a US session is extended hours."""

    return str(session or "") in {"pre_market", "after_market"}


def extended_hours_warning(session: str) -> str:
    """Return a practical warning for US extended hours."""

    if session == "pre_market":
        return (
            "현재 데이터는 프리장 기준일 수 있습니다. 프리장은 정규장보다 거래량이 적고 변동성이 클 수 있어 "
            "AI 판단은 참고용으로만 확인해 주세요."
        )
    if session == "after_market":
        return (
            "현재 데이터는 애프터장 기준일 수 있습니다. 애프터장 가격은 다음 정규장 흐름에서 다시 바뀔 수 있으므로 "
            "최종 매매 전 증권사 앱의 현재가와 호가를 확인해 주세요."
        )
    return ""
