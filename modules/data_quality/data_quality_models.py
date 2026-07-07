from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class MarketDataFreshness:
    """Freshness and quality metadata for one market data result."""

    ticker: str
    market: str
    data_timestamp: datetime | None
    query_timestamp: datetime
    age_minutes: float | None
    market_session: str
    freshness_status: str
    readiness_level: str
    is_trade_time: bool
    is_stale: bool
    is_realtime_claim_allowed: bool
    message: str


@dataclass(frozen=True)
class TradingReadinessResult:
    """Practical readiness result shown before using AI judgement as reference."""

    ticker: str
    name: str
    market: str
    is_ready_for_reference: bool
    readiness_level: str
    checklist: list[str]
    blocking_reasons: list[str]
    warning_messages: list[str]
    data_timestamp: datetime | None
    query_timestamp: datetime
    data_age_minutes: float | None
    price_status: str
    price_label: str
    freshness_status: str
    score_consistency_status: str
    sample_data_status: str
    market_session: str
    market_session_label: str
    is_extended_hours: bool
    extended_hours_type: str
    extended_hours_warning: str
    requires_extended_hours_confirmation: bool
    final_message: str


@dataclass(frozen=True)
class AuditResult:
    """Data quality audit result for developer checks."""

    passed: bool
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    checked_items: list[str] = field(default_factory=list)
    created_at: datetime | None = None
