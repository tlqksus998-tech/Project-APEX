from __future__ import annotations

import pandas as pd

from modules.scoring.confidence import as_optional_float

CHECK = "\u2705"
WARN = "\u26a0"


def classify_rsi(value: float | None) -> str:
    """Classify RSI into an explainable status."""

    if value is None:
        return f"{WARN} RSI : \ub370\uc774\ud130 \ubd80\uc871"
    if value < 30:
        return f"{CHECK} RSI : \uacfc\ub9e4\ub3c4"
    if value <= 60:
        return f"{CHECK} RSI : \uc911\ub9bd"
    if value <= 70:
        return f"{CHECK} RSI : \uc57d\uac04 \uacfc\uc5f4"
    return f"{WARN} RSI : \uacfc\uc5f4"


def classify_macd(status: str) -> str:
    """Classify MACD status into a reason line."""

    if status == "\uc0c1\uc2b9 \ubaa8\uba58\ud140":
        return f"{CHECK} MACD : \uc0c1\uc2b9 \ucd94\uc138"
    if status == "\ud558\ub77d \ubaa8\uba58\ud140":
        return f"{WARN} MACD : \ud558\ub77d \ubaa8\uba58\ud140"
    if status == "\uc911\ub9bd":
        return f"{CHECK} MACD : \uc911\ub9bd"
    return f"{WARN} MACD : \ub370\uc774\ud130 \ubd80\uc871"


def classify_volume(status: str) -> str:
    """Classify volume status into a reason line."""

    if status == "\uac70\ub798\ub7c9 \uc99d\uac00":
        return f"{CHECK} \uac70\ub798\ub7c9 \uc99d\uac00"
    if status == "\uac70\ub798\ub7c9 \uac10\uc18c":
        return f"{WARN} \uac70\ub798\ub7c9 \uac10\uc18c"
    if status == "\uac70\ub798\ub7c9 \ubcf4\ud1b5":
        return f"{CHECK} \uac70\ub798\ub7c9 \ubcf4\ud1b5"
    return f"{WARN} \uac70\ub798\ub7c9 : \ub370\uc774\ud130 \ubd80\uc871"


def classify_trend(status: str) -> str:
    """Classify trend status into a reason line."""

    if status == "\uc0c1\uc2b9\ucd94\uc138":
        return f"{CHECK} \uc7a5\uae30 \uc774\ub3d9\ud3c9\uade0\uc120 \uc704"
    if status == "\ud558\ub77d\ucd94\uc138":
        return f"{WARN} \uc774\ub3d9\ud3c9\uade0\uc120 \uc544\ub798 \ud750\ub984"
    if status == "\uc911\ub9bd":
        return f"{CHECK} \ucd94\uc138 : \uc911\ub9bd"
    return f"{WARN} \ucd94\uc138 : \ub370\uc774\ud130 \ubd80\uc871"


def classify_risk(risk: dict[str, object]) -> list[str]:
    """Create risk-related explanation lines."""

    lines: list[str] = []
    penalty = as_optional_float(risk.get("total_risk_penalty")) or 0.0
    if str(risk.get("concentration_risk") or "Normal") not in {"Normal", ""}:
        lines.append(f"{WARN} \ud604\uc7ac \ube44\uc911\uc774 \ub192\uc74c")
    if str(risk.get("cash_risk") or "Normal") not in {"Normal", ""}:
        lines.append(f"{WARN} \ud604\uae08 \ube44\uc911 \ubd80\uc871")
    if str(risk.get("leverage_risk") or "Normal") not in {"Normal", ""}:
        lines.append(f"{WARN} \ub808\ubc84\ub9ac\uc9c0 \uc704\ud5d8")
    if penalty == 0 and not lines:
        lines.append(f"{CHECK} \ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ub9ac\uc2a4\ud06c : \ubcf4\ud1b5")
    return lines


def build_decision_reasons(analysis: dict[str, object], risk: dict[str, object] | None = None) -> list[str]:
    """Return explainable reason lines for one ticker."""

    risk = risk or {}
    reasons = [
        classify_rsi(as_optional_float(analysis.get("rsi_14"))),
        classify_macd(str(analysis.get("macd_status") or "")),
        classify_volume(str(analysis.get("volume_status") or "")),
        classify_trend(str(analysis.get("trend_status") or "")),
    ]
    reasons.extend(classify_risk(risk))
    return reasons


def build_portfolio_reason_summary(analysis_results: pd.DataFrame, portfolio_risk: pd.DataFrame, limit: int = 5) -> list[str]:
    """Build compact portfolio-level reason summary for the home panel."""

    reasons: list[str] = []
    if analysis_results is not None and not analysis_results.empty:
        averages = {
            "rsi_14": pd.to_numeric(analysis_results.get("rsi_14"), errors="coerce").mean(),
        }
        first = analysis_results.iloc[0].to_dict()
        synthetic = {
            "rsi_14": averages["rsi_14"],
            "macd_status": most_common(analysis_results, "macd_status"),
            "volume_status": most_common(analysis_results, "volume_status"),
            "trend_status": most_common(analysis_results, "trend_status"),
        }
        if pd.isna(synthetic["rsi_14"]):
            synthetic["rsi_14"] = first.get("rsi_14")
        reasons.extend(build_decision_reasons(synthetic, {}))

    if portfolio_risk is not None and not portfolio_risk.empty:
        worst = portfolio_risk.sort_values("total_risk_penalty").iloc[0].to_dict()
        reasons.extend(classify_risk(worst))

    unique: list[str] = []
    for reason in reasons:
        if reason not in unique:
            unique.append(reason)
    return unique[:limit]


def most_common(data: pd.DataFrame, column: str) -> str:
    """Return the most common non-empty value from a DataFrame column."""

    if column not in data.columns:
        return ""
    values = data[column].dropna().astype(str)
    if values.empty:
        return ""
    return str(values.mode().iloc[0])
