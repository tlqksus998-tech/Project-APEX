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
