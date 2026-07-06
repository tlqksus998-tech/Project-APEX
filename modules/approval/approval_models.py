from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ApprovalDecision(StrEnum):
    """Future investment approval decisions."""

    BUY_APPROVED = "BUY APPROVED"
    WAIT = "WAIT"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    DO_NOT_BUY = "DO NOT BUY"


@dataclass(frozen=True)
class ApprovalResult:
    """Foundation model for future investment approval decisions."""

    ticker: str
    decision: ApprovalDecision
    reasons: list[str] = field(default_factory=list)
