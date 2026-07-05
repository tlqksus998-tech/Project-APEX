from __future__ import annotations

import pandas as pd

from modules.risk.risk_models import PortfolioRiskResult


LEVERAGE_KEYWORDS = ["????", "2X", "3X", "???", "???", "KORU", "TQQQ", "SOXL", "SQQQ"]


def evaluate_portfolio_risk(positions: pd.DataFrame, cash_amount: float = 0.0) -> pd.DataFrame:
    """Evaluate portfolio risk adjustments for each position."""

    if positions.empty:
        return pd.DataFrame(columns=["ticker", "concentration_risk", "cash_risk", "averaging_down_risk", "leverage_risk", "total_risk_penalty", "risk_messages"])

    total_current_value = float(pd.to_numeric(positions.get("current_value", 0.0), errors="coerce").fillna(0.0).sum())
    safe_cash = max(float(cash_amount or 0.0), 0.0)
    cash_ratio = safe_cash / (total_current_value + safe_cash) if (total_current_value + safe_cash) > 0 else 0.0

    results = []
    for _, row in positions.iterrows():
        result = evaluate_position_risk(row, cash_ratio)
        results.append(result.__dict__)
    return pd.DataFrame(results)


def evaluate_position_risk(row: pd.Series, cash_ratio: float) -> PortfolioRiskResult:
    """Evaluate risk adjustment for one position row."""

    ticker = str(row.get("ticker", "UNKNOWN"))
    name = str(row.get("name", ""))
    weight = safe_float(row.get("weight"))
    return_rate = safe_float(row.get("return_rate"))

    concentration_risk, concentration_penalty, concentration_message = score_concentration(weight)
    cash_risk, cash_penalty, cash_message = score_cash(cash_ratio)
    averaging_risk, averaging_penalty, averaging_message = score_averaging_down(return_rate)
    leverage_risk, leverage_penalty, leverage_message = score_leverage(ticker, name)

    messages = [message for message in [concentration_message, cash_message, averaging_message, leverage_message] if message]
    total_penalty = concentration_penalty + cash_penalty + averaging_penalty + leverage_penalty
    return PortfolioRiskResult(
        ticker=ticker,
        concentration_risk=concentration_risk,
        cash_risk=cash_risk,
        averaging_down_risk=averaging_risk,
        leverage_risk=leverage_risk,
        total_risk_penalty=total_penalty,
        risk_messages=messages,
    )


def score_concentration(weight: float) -> tuple[str, float, str]:
    """Score concentration risk from portfolio weight."""

    if weight >= 0.30:
        return "High Concentration Risk", -20.0, f"Position weight is {weight:.1%}, above 30%."
    if weight >= 0.20:
        return "Medium Concentration Risk", -10.0, f"Position weight is {weight:.1%}, above 20%."
    if weight >= 0.10:
        return "Low Concentration Risk", -5.0, f"Position weight is {weight:.1%}, above 10%."
    return "Normal", 0.0, ""


def score_cash(cash_ratio: float) -> tuple[str, float, str]:
    """Score cash buffer risk."""

    if cash_ratio < 0.05:
        return "High Cash Risk", -15.0, f"Cash ratio is {cash_ratio:.1%}, below 5%."
    if cash_ratio < 0.10:
        return "Medium Cash Risk", -10.0, f"Cash ratio is {cash_ratio:.1%}, below 10%."
    if cash_ratio < 0.20:
        return "Low Cash Risk", -5.0, f"Cash ratio is {cash_ratio:.1%}, below 20%."
    return "Normal", 0.0, ""


def score_averaging_down(return_rate: float) -> tuple[str, float, str]:
    """Score averaging-down risk from unrealized return."""

    if return_rate <= -0.15:
        return "High Averaging Down Risk", -15.0, f"Return is {return_rate:.1%}, below -15%."
    if return_rate <= -0.10:
        return "Medium Averaging Down Risk", -10.0, f"Return is {return_rate:.1%}, below -10%."
    if return_rate <= -0.05:
        return "Low Averaging Down Risk", -5.0, f"Return is {return_rate:.1%}, below -5%."
    return "Normal", 0.0, ""


def score_leverage(ticker: str, name: str) -> tuple[str, float, str]:
    """Score leverage product risk from ticker and name keywords."""

    target = f"{ticker} {name}".upper()
    for keyword in LEVERAGE_KEYWORDS:
        if keyword.upper() in target:
            return "Leverage Risk", -15.0, f"Leverage keyword detected: {keyword}."
    return "Normal", 0.0, ""


def safe_float(value: object) -> float:
    """Convert a value to float with fallback to zero."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if pd.isna(numeric):
        return 0.0
    return numeric
