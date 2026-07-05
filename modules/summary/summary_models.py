from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PortfolioSummaryResult:
    """Rule-based portfolio-level AI summary result."""

    overall_score: float
    overall_decision: str
    risk_level: str
    summary_text: str
    key_strengths: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    confidence: float = 0.0
