from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioRiskResult:
    """Portfolio risk adjustment result for one ticker."""

    ticker: str
    concentration_risk: str
    cash_risk: str
    averaging_down_risk: str
    leverage_risk: str
    total_risk_penalty: float
    risk_messages: list[str]
