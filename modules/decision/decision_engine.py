from __future__ import annotations

import pandas as pd

from modules.analysis.analysis_engine import (
    MACD_DOWN,
    MACD_UP,
    STATUS_INSUFFICIENT,
    STATUS_NEUTRAL,
    TREND_DOWN,
    TREND_UP,
    VOLUME_DOWN,
    VOLUME_NORMAL,
    VOLUME_UP,
)
from modules.decision.decision_models import DecisionCode, DecisionResult


def decide_one(analysis: dict[str, object], risk: dict[str, object] | None = None) -> DecisionResult:
    """Create one rule-based decision result from technical analysis and portfolio risk."""

    risk = risk or {}
    ticker = str(analysis.get("ticker") or risk.get("ticker") or "UNKNOWN")
    score = 45.0
    reasons: list[str] = []

    rsi_score, rsi_reason = score_rsi(as_optional_float(analysis.get("rsi_14")))
    trend_score, trend_reason = score_trend(str(analysis.get("trend_status") or STATUS_INSUFFICIENT))
    macd_score, macd_reason = score_macd(str(analysis.get("macd_status") or STATUS_INSUFFICIENT))
    volume_score, volume_reason = score_volume(str(analysis.get("volume_status") or STATUS_INSUFFICIENT))
    week52_score, week52_reason = score_week52(as_optional_float(analysis.get("week52_position")))

    score += rsi_score + trend_score + macd_score + volume_score + week52_score
    reasons.extend([rsi_reason, trend_reason, macd_reason, volume_reason, week52_reason])

    decision_score = clamp(score, 0.0, 100.0)
    risk_penalty = min(as_optional_float(risk.get("total_risk_penalty")) or 0.0, 0.0)
    final_score = clamp(decision_score + risk_penalty, 0.0, 100.0)
    confidence_score = calculate_confidence(analysis)
    decision = map_decision(final_score)
    risk_messages = risk.get("risk_messages") if isinstance(risk.get("risk_messages"), list) else []
    return DecisionResult(ticker, decision, decision_score, risk_penalty, final_score, confidence_score, reasons, risk_messages)


def decide_many(analysis_results: pd.DataFrame, risk_results: pd.DataFrame | None = None) -> pd.DataFrame:
    """Create decision results for all rows in an analysis DataFrame."""

    columns = ["ticker", "decision", "decision_score", "risk_penalty", "final_score", "confidence_score", "reasons", "risk_messages"]
    if analysis_results.empty:
        return pd.DataFrame(columns=columns)

    risk_by_ticker = build_risk_lookup(risk_results)
    rows = []
    for record in analysis_results.to_dict(orient="records"):
        ticker = str(record.get("ticker") or "UNKNOWN")
        result = decide_one(record, risk_by_ticker.get(ticker, {}))
        rows.append(
            {
                "ticker": result.ticker,
                "decision": result.decision.value,
                "decision_score": result.decision_score,
                "risk_penalty": result.risk_penalty,
                "final_score": result.final_score,
                "confidence_score": result.confidence_score,
                "reasons": result.reasons,
                "risk_messages": result.risk_messages,
            }
        )
    return pd.DataFrame(rows, columns=columns)


def build_risk_lookup(risk_results: pd.DataFrame | None) -> dict[str, dict[str, object]]:
    """Build ticker-indexed risk records."""

    if risk_results is None or risk_results.empty:
        return {}
    return {str(row["ticker"]): row for row in risk_results.to_dict(orient="records")}


def score_rsi(rsi: float | None) -> tuple[float, str]:
    """Score RSI contribution."""

    if rsi is None:
        return 0.0, "RSI data is insufficient."
    if rsi < 30:
        return 20.0, f"RSI is {rsi:.1f}, indicating an oversold area."
    if rsi <= 60:
        return 15.0, f"RSI is {rsi:.1f}, inside a stable range."
    if rsi <= 70:
        return 5.0, f"RSI is {rsi:.1f}, slightly elevated."
    return -10.0, f"RSI is {rsi:.1f}, indicating an overheated area."


def score_trend(trend_status: str) -> tuple[float, str]:
    """Score trend contribution."""

    if trend_status == TREND_UP:
        return 20.0, "Trend status is upward."
    if trend_status == STATUS_NEUTRAL:
        return 10.0, "Trend status is neutral."
    if trend_status == TREND_DOWN:
        return -10.0, "Trend status is downward."
    return 0.0, "Trend data is insufficient."


def score_macd(macd_status: str) -> tuple[float, str]:
    """Score MACD contribution."""

    if macd_status == MACD_UP:
        return 15.0, "MACD shows upward momentum."
    if macd_status == STATUS_NEUTRAL:
        return 5.0, "MACD is neutral."
    if macd_status == MACD_DOWN:
        return -10.0, "MACD shows downward momentum."
    return 0.0, "MACD data is insufficient."


def score_volume(volume_status: str) -> tuple[float, str]:
    """Score volume contribution."""

    if volume_status == VOLUME_UP:
        return 10.0, "Volume is increasing."
    if volume_status == VOLUME_NORMAL:
        return 5.0, "Volume is normal."
    if volume_status == VOLUME_DOWN:
        return -5.0, "Volume is decreasing."
    return 0.0, "Volume data is insufficient."


def score_week52(position: float | None) -> tuple[float, str]:
    """Score 52-week position contribution."""

    if position is None:
        return 0.0, "52-week position data is insufficient."
    if 20 <= position <= 80:
        return 10.0, f"52-week position is {position:.1f}, inside a neutral range."
    if position > 80:
        return -5.0, f"52-week position is {position:.1f}, near the upper range."
    return 5.0, f"52-week position is {position:.1f}, near the lower range."


def calculate_confidence(analysis: dict[str, object]) -> float:
    """Calculate confidence score based on available analysis fields."""

    confidence = 0.0
    if as_optional_float(analysis.get("rsi_14")) is not None:
        confidence += 20.0
    if str(analysis.get("trend_status") or STATUS_INSUFFICIENT) != STATUS_INSUFFICIENT:
        confidence += 20.0
    if as_optional_float(analysis.get("macd")) is not None and str(analysis.get("macd_status") or STATUS_INSUFFICIENT) != STATUS_INSUFFICIENT:
        confidence += 20.0
    if as_optional_float(analysis.get("volume_ratio")) is not None and str(analysis.get("volume_status") or STATUS_INSUFFICIENT) != STATUS_INSUFFICIENT:
        confidence += 20.0
    if as_optional_float(analysis.get("week52_position")) is not None:
        confidence += 20.0
    return clamp(confidence, 0.0, 100.0)


def map_decision(decision_score: float) -> DecisionCode:
    """Map numeric score to a decision code."""

    if decision_score >= 85:
        return DecisionCode.STRONG_BUY
    if decision_score >= 70:
        return DecisionCode.BUY
    if decision_score >= 45:
        return DecisionCode.HOLD
    if decision_score >= 30:
        return DecisionCode.REDUCE
    return DecisionCode.SELL


def as_optional_float(value: object) -> float | None:
    """Convert a value to float or None."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value to an inclusive range."""

    return max(minimum, min(maximum, value))
