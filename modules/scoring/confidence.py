from __future__ import annotations

import pandas as pd

STATUS_INSUFFICIENT = "\ub370\uc774\ud130 \ubd80\uc871"


def as_optional_float(value: object) -> float | None:
    """Convert a value to float or None."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Clamp a numeric value to an inclusive range."""

    return max(minimum, min(maximum, value))


def calculate_confidence_score(analysis: dict[str, object]) -> float:
    """Calculate AI confidence from available analysis fields."""

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
    return clamp(confidence)


def portfolio_confidence(decision_results: pd.DataFrame) -> float:
    """Return average confidence for portfolio-level explanation."""

    if decision_results is None or decision_results.empty or "confidence_score" not in decision_results.columns:
        return 0.0
    values = pd.to_numeric(decision_results["confidence_score"], errors="coerce").dropna()
    if values.empty:
        return 0.0
    return clamp(float(values.mean()))
