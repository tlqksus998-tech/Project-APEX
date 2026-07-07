from __future__ import annotations

from datetime import datetime

from modules.data_quality.data_quality_models import MarketDataFreshness
from modules.data_quality.market_clock import get_market_session, is_korean_market, market_timezone, normalize_market_datetime

INVALID_SOURCE_TOKENS = {"fallback", "sample", "demo", "mock", "dummy", "placeholder", "example"}


def is_decision_source_allowed(source: str, success: bool = True) -> bool:
    """Return whether a provider source can be used for AI judgement."""

    if not success:
        return False
    normalized = str(source or "").strip().lower()
    if not normalized:
        return False
    return not any(token in normalized for token in INVALID_SOURCE_TOKENS)


def assess_market_data_freshness(
    ticker: str,
    market: str,
    data_timestamp: datetime | None,
    query_timestamp: datetime | None = None,
) -> MarketDataFreshness:
    """Assess whether market data is fresh enough for AI judgement."""

    zone = market_timezone(market)
    query_time = query_timestamp.astimezone(zone) if query_timestamp and query_timestamp.tzinfo else (query_timestamp.replace(tzinfo=zone) if query_timestamp else datetime.now(zone))
    session, is_trade_time = get_market_session(market, query_time)
    data_time = normalize_market_datetime(data_timestamp, market)

    if data_time is None:
        return MarketDataFreshness(
            ticker=ticker,
            market=market,
            data_timestamp=None,
            query_timestamp=query_time,
            age_minutes=None,
            market_session=session,
            freshness_status="unknown",
            readiness_level="BLOCKED",
            is_trade_time=is_trade_time,
            is_stale=True,
            is_realtime_claim_allowed=False,
            message="데이터 기준 시간을 확인할 수 없어 AI 판단 신뢰도가 낮습니다.",
        )

    age_minutes = max(0.0, (query_time - data_time).total_seconds() / 60.0)
    same_trade_date = data_time.date() == query_time.date()

    if is_trade_time:
        if age_minutes <= 30:
            status = "fresh"
            message = "최근 조회 기준 데이터입니다."
            stale = False
        elif age_minutes <= 60:
            status = "delayed"
            message = "지연 가능성이 있는 데이터입니다."
            stale = False
        elif not is_korean_market(market) and same_trade_date and age_minutes <= 60 * 24:
            status = "delayed"
            message = "미국 주식 일봉 기준 데이터입니다. 정규장 중 실시간 시세가 아닐 수 있어 주의가 필요합니다."
            stale = False
        else:
            status = "stale"
            message = "데이터가 오래되어 AI 판단을 제한합니다."
            stale = True
    else:
        if same_trade_date or age_minutes <= 60 * 24 * 4:
            status = "closed_market"
            message = "최근 조회 기준이며, 현재 실시간 시세가 아닐 수 있습니다."
            stale = False
        else:
            status = "stale"
            message = "데이터 기준 시간이 오래되어 AI 판단을 제한합니다."
            stale = True

    return MarketDataFreshness(
        ticker=ticker,
        market=market,
        data_timestamp=data_time,
        query_timestamp=query_time,
        age_minutes=age_minutes,
        market_session=session,
        freshness_status=status,
        readiness_level=readiness_level(status),
        is_trade_time=is_trade_time,
        is_stale=stale,
        is_realtime_claim_allowed=status == "fresh",
        message=message,
    )


def readiness_level(status: str) -> str:
    """Map freshness status to a display and filtering readiness level."""

    if status == "fresh":
        return "READY"
    if status in {"delayed", "closed_market"}:
        return "CAUTION"
    return "BLOCKED"
