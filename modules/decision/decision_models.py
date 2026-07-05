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
