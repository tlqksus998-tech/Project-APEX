from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

import pandas as pd

from modules.ai_judgement import AIJudgementSummary, build_ai_judgement_summary
from modules.analysis.analysis_engine import TechnicalAnalysisResult, analyze_ohlcv
from modules.config import get_config
from modules.data_quality import MarketDataFreshness, TradingReadinessResult, assess_market_data_freshness, build_trading_readiness, is_decision_source_allowed
from modules.decision.decision_engine import decide_one
from modules.decision.decision_models import DecisionResult
from modules.market.market_models import MarketDataRequest, OHLCVDataResult, PriceData
from modules.market.master_loader import load_master_database
from modules.market.ohlcv_provider import get_ohlcv
from modules.market.price_provider import get_current_price

SEOUL = ZoneInfo("Asia/Seoul")

DEFAULT_KOSPI_CANDIDATES = [
    ("삼성전자", "005930", "KOSPI"),
    ("삼성전기", "009150", "KOSPI"),
    ("SK하이닉스", "000660", "KOSPI"),
    ("SK스퀘어", "402340", "KOSPI"),
    ("현대차", "005380", "KOSPI"),
    ("NAVER", "035420", "KOSPI"),
    ("카카오", "035720", "KOSPI"),
    ("POSCO홀딩스", "005490", "KOSPI"),
    ("LG에너지솔루션", "373220", "KOSPI"),
    ("삼성바이오로직스", "207940", "KOSPI"),
    ("기아", "000270", "KOSPI"),
    ("셀트리온", "068270", "KOSPI"),
]

DEFAULT_KOSDAQ_CANDIDATES = [
    ("알테오젠", "196170", "KOSDAQ"),
    ("에코프로비엠", "247540", "KOSDAQ"),
    ("에코프로", "086520", "KOSDAQ"),
    ("HLB", "028300", "KOSDAQ"),
    ("레인보우로보틱스", "277810", "KOSDAQ"),
    ("펄어비스", "263750", "KOSDAQ"),
    ("카카오게임즈", "293490", "KOSDAQ"),
    ("넥슨게임즈", "225570", "KOSDAQ"),
    ("미래에셋벤처투자", "100790", "KOSDAQ"),
    ("JYP Ent.", "035900", "KOSDAQ"),
    ("에스엠", "041510", "KOSDAQ"),
    ("원익IPS", "240810", "KOSDAQ"),
]

DEFAULT_NASDAQ_CANDIDATES = [
    ("NVIDIA", "NVDA", "NASDAQ"),
    ("Microsoft", "MSFT", "NASDAQ"),
    ("Apple", "AAPL", "NASDAQ"),
    ("Amazon", "AMZN", "NASDAQ"),
    ("Alphabet", "GOOGL", "NASDAQ"),
    ("Meta Platforms", "META", "NASDAQ"),
    ("Tesla", "TSLA", "NASDAQ"),
    ("Broadcom", "AVGO", "NASDAQ"),
    ("AMD", "AMD", "NASDAQ"),
    ("Taiwan Semiconductor", "TSM", "NYSE"),
    ("ASML", "ASML", "NASDAQ"),
    ("Netflix", "NFLX", "NASDAQ"),
    ("Costco", "COST", "NASDAQ"),
    ("Palantir", "PLTR", "NASDAQ"),
    ("Invesco QQQ", "QQQ", "NASDAQ"),
    ("Micron", "MU", "NASDAQ"),
    ("Arm Holdings", "ARM", "NASDAQ"),
    ("Super Micro Computer", "SMCI", "NASDAQ"),
    ("Oracle", "ORCL", "NYSE"),
    ("CrowdStrike", "CRWD", "NASDAQ"),
]


@dataclass(frozen=True)
class UnifiedAIJudgementResult:
    """Common result used by stock detail and AI ranking views."""

    ticker: str
    name: str
    market: str
    ai_score: float | None
    final_signal: str
    signal_label: str
    one_line_summary: str
    beginner_summary: str
    detail_summary: str
    updated_at: str
    data_timestamp: str
    source: str
    success: bool
    is_fallback: bool
    error_message: str
    data_quality_status: str = "unknown"
    freshness_status: str = "unknown"
    readiness_level: str = "BLOCKED"
    data_age_minutes: float | None = None
    query_timestamp: str = ""
    data_warning_message: str = ""
    is_decision_allowed: bool = True
    price_label: str = ""
    market_session: str = "unknown"
    market_session_label: str = "확인 필요"
    is_extended_hours: bool = False
    extended_hours_type: str = ""
    extended_hours_warning: str = ""
    final_checklist: list[str] | None = None
    readiness: TradingReadinessResult | None = None
    price: PriceData | None = None
    ohlcv: OHLCVDataResult | None = None
    analysis: TechnicalAnalysisResult | None = None
    decision: DecisionResult | None = None
    summary: AIJudgementSummary | None = None


def get_unified_ai_judgement(name: str, ticker: str, market: str = "") -> UnifiedAIJudgementResult:
    """Return the shared judgement result for ranking and detail pages."""

    return _get_unified_ai_judgement_cached(str(name or ticker), str(ticker), str(market or ""))


@lru_cache(maxsize=256)
def _get_unified_ai_judgement_cached(name: str, ticker: str, market: str) -> UnifiedAIJudgementResult:
    """Build a cached judgement result using the existing analysis and decision engines."""

    query_dt = now_datetime()
    updated_at = format_dt(query_dt)
    try:
        config = get_config()
        price = get_current_price(ticker, config, market_hint=market)
        ohlcv = get_ohlcv(MarketDataRequest(ticker=ticker, period="6mo", interval="1d", market_hint=market), config)
        source = " / ".join(sorted({str(price.source), str(ohlcv.source)}))
        data_dt = extract_latest_data_datetime(ohlcv.data)
        freshness = assess_market_data_freshness(ticker, market or price.market, data_dt, query_dt)

        source_allowed = is_decision_source_allowed(source, bool(price.success and ohlcv.success))
        base_readiness = build_trading_readiness(ticker, name, market or price.market, source, bool(price.success and ohlcv.success), freshness)
        if not source_allowed:
            return unavailable_result(name, ticker, market or price.market, source, price, ohlcv, freshness, "실제 시장 데이터가 아니어서 AI 판단을 제공하지 않습니다.", readiness=base_readiness)
        if freshness.is_stale or freshness.freshness_status in {"unknown", "invalid"}:
            return unavailable_result(name, ticker, market or price.market, source, price, ohlcv, freshness, freshness.message, readiness=base_readiness)

        analysis = analyze_ohlcv(ticker, ohlcv.data)
        if not analysis.success:
            return unavailable_result(name, ticker, market or price.market, source, price, ohlcv, freshness, analysis.message, analysis=analysis, readiness=base_readiness)

        decision = decide_one(analysis.__dict__)
        decision_dict = decision.__dict__ | {
            "decision": decision.decision.value,
            "final_decision": decision.final_decision,
            "stock_signal": decision.stock_signal,
        }
        summary = build_ai_judgement_summary(name, ticker, analysis.__dict__, decision_dict)
        readiness = build_trading_readiness(ticker, name, market or price.market, source, True, freshness, ai_score=float(decision.final_score))
        return UnifiedAIJudgementResult(
            ticker=ticker,
            name=name,
            market=market or price.market,
            ai_score=float(decision.final_score),
            final_signal=str(decision.final_decision),
            signal_label=str(decision.final_decision),
            one_line_summary=str(summary.one_line_conclusion),
            beginner_summary=str(decision.beginner_summary or summary.beginner_explanation),
            detail_summary=str(summary.detailed_summary),
            updated_at=updated_at,
            data_timestamp=format_dt(freshness.data_timestamp),
            source=source,
            success=True,
            is_fallback=False,
            error_message="",
            data_quality_status="usable",
            freshness_status=freshness.freshness_status,
            readiness_level=readiness.readiness_level,
            data_age_minutes=freshness.age_minutes,
            query_timestamp=format_dt(freshness.query_timestamp),
            data_warning_message=" / ".join(readiness.warning_messages) if readiness.warning_messages else freshness.message,
            is_decision_allowed=readiness.is_ready_for_reference,
            price_label=readiness.price_label,
            market_session=readiness.market_session,
            market_session_label=readiness.market_session_label,
            is_extended_hours=readiness.is_extended_hours,
            extended_hours_type=readiness.extended_hours_type,
            extended_hours_warning=readiness.extended_hours_warning,
            final_checklist=readiness.checklist,
            readiness=readiness,
            price=price,
            ohlcv=ohlcv,
            analysis=analysis,
            decision=decision,
            summary=summary,
        )
    except Exception as exc:
        return UnifiedAIJudgementResult(
            ticker=ticker or "UNKNOWN",
            name=name or ticker or "알 수 없는 종목",
            market=market or "UNKNOWN",
            ai_score=None,
            final_signal="DATA_UNAVAILABLE",
            signal_label="판단 보류",
            one_line_summary="데이터를 충분히 가져오지 못해 AI 판단을 제공하지 않습니다.",
            beginner_summary="잠시 후 다시 확인해 주세요.",
            detail_summary="공통 AI 판단 엔진 실행 중 오류가 발생했습니다.",
            updated_at=updated_at,
            data_timestamp="확인 불가",
            source="fallback",
            success=False,
            is_fallback=True,
            error_message=f"{exc.__class__.__name__}",
            data_quality_status="invalid",
            freshness_status="unknown",
            readiness_level="BLOCKED",
            query_timestamp=updated_at,
            data_warning_message="데이터 조회 실패로 AI 판단을 제한합니다.",
            is_decision_allowed=False,
            price_label="가격 기준 확인 불가",
        )


def unavailable_result(
    name: str,
    ticker: str,
    market: str,
    source: str,
    price: PriceData | None,
    ohlcv: OHLCVDataResult | None,
    freshness: MarketDataFreshness,
    message: str,
    analysis: TechnicalAnalysisResult | None = None,
    readiness: TradingReadinessResult | None = None,
) -> UnifiedAIJudgementResult:
    """Return a safe non-scored result when data quality is insufficient."""

    readiness = readiness or build_trading_readiness(ticker, name, market, source, False, freshness)
    return UnifiedAIJudgementResult(
        ticker=ticker or "UNKNOWN",
        name=name or ticker or "알 수 없는 종목",
        market=market or "UNKNOWN",
        ai_score=None,
        final_signal="DATA_UNAVAILABLE",
        signal_label="판단 보류",
        one_line_summary=message or "데이터 문제로 AI 판단을 제공하지 않습니다.",
        beginner_summary="데이터를 다시 조회한 뒤 판단을 확인해 주세요.",
        detail_summary="fallback, sample, stale, unknown 데이터는 AI 점수 계산에 사용하지 않습니다.",
        updated_at=format_dt(freshness.query_timestamp),
        data_timestamp=format_dt(freshness.data_timestamp) if freshness.data_timestamp else "확인 불가",
        source=source or "unknown",
        success=False,
        is_fallback=True,
        error_message=message,
        data_quality_status="blocked",
        freshness_status=freshness.freshness_status,
        readiness_level=readiness.readiness_level,
        data_age_minutes=freshness.age_minutes,
        query_timestamp=format_dt(freshness.query_timestamp),
        data_warning_message=message or readiness.final_message,
        is_decision_allowed=False,
        price_label=readiness.price_label,
        market_session=readiness.market_session,
        market_session_label=readiness.market_session_label,
        is_extended_hours=readiness.is_extended_hours,
        extended_hours_type=readiness.extended_hours_type,
        extended_hours_warning=readiness.extended_hours_warning,
        final_checklist=readiness.checklist,
        readiness=readiness,
        price=price,
        ohlcv=ohlcv,
        analysis=analysis,
    )


def build_ai_ranking(market: str, limit: int = 10, candidate_limit: int = 24) -> pd.DataFrame:
    """Build a market ranking sorted by the shared AI score."""

    rows: list[dict[str, object]] = []
    excluded_count = 0
    for name, ticker, candidate_market in select_candidate_pool(market, candidate_limit):
        result = get_unified_ai_judgement(name, ticker, candidate_market)
        if not result.is_decision_allowed or result.ai_score is None or result.is_fallback or not result.success:
            excluded_count += 1
            continue
        rows.append(result_to_row(result))

    if not rows:
        return pd.DataFrame(columns=ranking_columns()).assign(excluded_count=excluded_count)

    frame = pd.DataFrame(rows)
    frame["ai_score"] = pd.to_numeric(frame["ai_score"], errors="coerce")
    frame = frame.dropna(subset=["ai_score"])
    frame = frame.sort_values(["ai_score", "ticker"], ascending=[False, True]).head(limit).reset_index(drop=True)
    frame.insert(0, "rank", range(1, len(frame) + 1))
    frame["excluded_count"] = excluded_count
    return frame[ranking_columns()]


def select_candidate_pool(market: str, candidate_limit: int = 24) -> list[tuple[str, str, str]]:
    """Select a bounded candidate pool for one ranking market."""

    normalized = str(market or "").upper()
    defaults = default_candidates(normalized)
    master_candidates = master_candidates_for_market(normalized, candidate_limit)

    seen: set[tuple[str, str]] = set()
    candidates: list[tuple[str, str, str]] = []
    for item in [*defaults, *master_candidates]:
        key = (item[1], item[2])
        if key in seen:
            continue
        seen.add(key)
        candidates.append(item)
        if len(candidates) >= candidate_limit:
            break
    return candidates


def master_candidates_for_market(market: str, candidate_limit: int) -> list[tuple[str, str, str]]:
    """Load candidates from the market master database with fallback on failure."""

    try:
        master = load_master_database()
    except Exception:
        return []
    if master.empty:
        return []

    frame = master.copy()
    frame["market"] = frame.get("market", "").astype(str)
    frame["asset_type"] = frame.get("asset_type", "").astype(str).str.upper()
    if market in {"KOSPI", "KOSDAQ"}:
        frame = frame[frame["market"].str.upper().str.contains(market, na=False)]
    elif market == "NASDAQ":
        frame = frame[frame["market"].str.upper().str.contains("NASDAQ", na=False)]
    else:
        frame = frame[frame["market"].str.upper().str.contains(market, na=False)]
    frame = frame[frame["asset_type"].isin(["STOCK", "ETF"])]
    rows: list[tuple[str, str, str]] = []
    for row in frame.head(candidate_limit).itertuples(index=False):
        rows.append((str(row.name), str(row.ticker), str(row.market)))
    return rows


def default_candidates(market: str) -> list[tuple[str, str, str]]:
    """Return the representative fallback candidate list for one market."""

    if market == "KOSDAQ":
        return DEFAULT_KOSDAQ_CANDIDATES
    if market == "NASDAQ":
        return DEFAULT_NASDAQ_CANDIDATES
    return DEFAULT_KOSPI_CANDIDATES


def result_to_row(result: UnifiedAIJudgementResult) -> dict[str, object]:
    """Convert a unified result to a ranking row."""

    return {
        "name": result.name,
        "ticker": result.ticker,
        "market": result.market,
        "ai_score": result.ai_score,
        "final_signal": result.final_signal,
        "one_line_summary": result.one_line_summary,
        "data_timestamp": result.data_timestamp,
        "query_timestamp": result.query_timestamp,
        "updated_at": result.updated_at,
        "source": result.source,
        "freshness_status": result.freshness_status,
        "readiness_level": result.readiness_level,
        "data_age_minutes": result.data_age_minutes,
        "price_label": result.price_label,
        "market_session": result.market_session,
        "market_session_label": result.market_session_label,
        "is_extended_hours": result.is_extended_hours,
        "extended_hours_warning": result.extended_hours_warning,
        "success": result.success,
        "is_fallback": result.is_fallback,
        "is_decision_allowed": result.is_decision_allowed,
        "error_message": result.error_message,
        "excluded_count": 0,
    }


def ranking_columns() -> list[str]:
    """Return the public ranking table columns."""

    return [
        "rank",
        "name",
        "ticker",
        "market",
        "ai_score",
        "final_signal",
        "one_line_summary",
        "data_timestamp",
        "query_timestamp",
        "updated_at",
        "source",
        "freshness_status",
        "readiness_level",
        "data_age_minutes",
        "price_label",
        "market_session",
        "market_session_label",
        "is_extended_hours",
        "extended_hours_warning",
        "success",
        "is_fallback",
        "is_decision_allowed",
        "error_message",
        "excluded_count",
    ]


def extract_latest_data_datetime(data: pd.DataFrame) -> datetime | None:
    """Return the latest OHLCV datetime when available."""

    if data is None or data.empty or "date" not in data.columns:
        return None
    latest = pd.to_datetime(data["date"], errors="coerce").dropna()
    if latest.empty:
        return None
    value = latest.max()
    return value.to_pydatetime() if hasattr(value, "to_pydatetime") else value


def extract_data_timestamp(data: pd.DataFrame) -> str:
    """Return the latest OHLCV date as display text."""

    return format_dt(extract_latest_data_datetime(data))


def format_dt(value: datetime | None) -> str:
    """Format a datetime for display."""

    if value is None:
        return "확인 불가"
    localized = value.astimezone(SEOUL) if value.tzinfo else value.replace(tzinfo=SEOUL)
    return localized.strftime("%Y-%m-%d %H:%M")


def build_error_message(price: PriceData, ohlcv: OHLCVDataResult, analysis: TechnicalAnalysisResult) -> str:
    """Build a compact fallback message from provider statuses."""

    messages = [price.message, ohlcv.message, analysis.message]
    return " / ".join(str(message) for message in messages if str(message or "").strip())


def now_datetime() -> datetime:
    """Return current Seoul datetime."""

    return datetime.now(SEOUL)


def now_text() -> str:
    """Return current Seoul timestamp for display."""

    return format_dt(now_datetime())


def clear_ai_judgement_cache() -> None:
    """Clear cached unified judgement results."""

    _get_unified_ai_judgement_cached.cache_clear()
