from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DecisionCode(StrEnum):
    """Supported decision labels for Sprint 2.6."""

    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    SELL = "SELL"


class StockSignal(StrEnum):
    """Stock-only technical signal labels."""

    STRONG_BUY = "STRONG BUY"
    BUY = "BUY"
    WATCH = "WATCH"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    SELL = "SELL"


class FinalDecision(StrEnum):
    """Final action labels after market, risk, and portfolio fit overrides."""

    BUY_APPROVED = "BUY APPROVED"
    BUY = "BUY"
    WATCH = "WATCH"
    WAIT = "WAIT"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    SELL = "SELL"
    DO_NOT_BUY = "DO NOT BUY"


@dataclass(frozen=True)
class DecisionResult:
    """Decision Engine result for one ticker."""

    ticker: str
    decision: DecisionCode
    decision_score: float
    risk_penalty: float
    final_score: float
    confidence_score: float
    reasons: list[str]
    risk_messages: list[str]
    stock_signal: str = "HOLD"
    final_decision: str = "HOLD"
    action: str = "보유 또는 관찰"
    score: float = 45.0
    confidence: float = 50.0
    market_regime: str = "NEUTRAL"
    stock_score: float = 45.0
    trend_score: float = 50.0
    momentum_score: float = 50.0
    volume_score: float = 50.0
    risk_score: float = 100.0
    portfolio_fit_score: float = 100.0
    warnings: list[str] | None = None
    action_guide: str = ""
    beginner_summary: str = ""
    advanced_summary: str = ""
