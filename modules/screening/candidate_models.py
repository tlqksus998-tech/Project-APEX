from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CandidateStock:
    """Today candidate stock result."""

    name: str
    ticker: str
    market: str
    final_score: float
    decision: str
    reasons: list[str] = field(default_factory=list)
