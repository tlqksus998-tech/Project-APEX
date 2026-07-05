from __future__ import annotations

import pandas as pd

from modules.summary.summary_models import PortfolioSummaryResult

BUY_DECISIONS = {"STRONG_BUY", "BUY"}
REDUCE_DECISIONS = {"REDUCE", "SELL"}


def generate_portfolio_summary(
    metrics: dict[str, float] | None,
    positions: pd.DataFrame | None,
    decision_results: pd.DataFrame | None,
    risk_results: pd.DataFrame | None,
    cash_amount: float = 0.0,
) -> PortfolioSummaryResult:
    """Generate a rule-based AI-style portfolio summary without external APIs."""

    metrics = metrics or {}
    positions = positions if positions is not None else pd.DataFrame()
    decision_results = decision_results if decision_results is not None else pd.DataFrame()
    risk_results = risk_results if risk_results is not None else pd.DataFrame()

    if positions.empty and decision_results.empty:
        return PortfolioSummaryResult(
            overall_score=0.0,
            overall_decision="HOLD",
            risk_level="Low",
            summary_text="\uc544\uc9c1 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\uac00 \uc5c6\uc5b4 \uc885\ud569 \ud310\ub2e8\uc744 \ubcf4\ub958\ud569\ub2c8\ub2e4. \uba3c\uc800 \uc885\ubaa9\uc744 \ucd94\uac00\ud574 \ubd84\uc11d\uc744 \uc2dc\uc791\ud558\uc138\uc694.",
            key_strengths=["\uc704\ud5d8\uc774 \uacc4\uc0b0\ub420 \ubcf4\uc720 \uc885\ubaa9\uc774 \uc544\uc9c1 \uc5c6\uc2b5\ub2c8\ub2e4."],
            key_risks=["\ubd84\uc11d\uc5d0 \ud544\uc694\ud55c \ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ub370\uc774\ud130\uac00 \ubd80\uc871\ud569\ub2c8\ub2e4."],
            action_items=["\uc885\ubaa9\uc744 \uac80\uc0c9\ud574 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\uc5d0 \ucd94\uac00\ud558\uc138\uc694."],
            confidence=20.0,
        )

    stats = calculate_summary_stats(metrics, positions, decision_results, risk_results, cash_amount)
    overall_score = calculate_overall_score(stats)
    overall_decision = map_overall_decision(overall_score, stats)
    risk_level = map_risk_level(stats)
    strengths = build_key_strengths(stats)
    risks = build_key_risks(stats)
    actions = build_action_items(stats, overall_decision)
    summary_text = build_summary_text(overall_decision, risk_level, stats)
    confidence = calculate_summary_confidence(stats)

    return PortfolioSummaryResult(overall_score, overall_decision, risk_level, summary_text, strengths, risks, actions, confidence)


def calculate_summary_stats(metrics: dict[str, float], positions: pd.DataFrame, decision_results: pd.DataFrame, risk_results: pd.DataFrame, cash_amount: float) -> dict[str, float | bool]:
    """Calculate portfolio-level summary statistics."""

    final_scores = pd.to_numeric(decision_results.get("final_score", pd.Series(dtype=float)), errors="coerce").dropna()
    decisions = decision_results.get("decision", pd.Series(dtype=str)).fillna("").astype(str).str.upper() if not decision_results.empty else pd.Series(dtype=str)
    total_value = float(metrics.get("total_current_value", 0.0) or 0.0)
    safe_cash = max(float(cash_amount or 0.0), 0.0)
    cash_ratio = safe_cash / (safe_cash + total_value) if (safe_cash + total_value) > 0 else 0.0
    concentration = float(pd.to_numeric(positions.get("weight", pd.Series(dtype=float)), errors="coerce").fillna(0.0).max()) if not positions.empty else 0.0
    return_rates = pd.to_numeric(positions.get("return_rate", pd.Series(dtype=float)), errors="coerce").fillna(0.0) if not positions.empty else pd.Series(dtype=float)
    penalties = pd.to_numeric(risk_results.get("total_risk_penalty", pd.Series(dtype=float)), errors="coerce").fillna(0.0) if not risk_results.empty else pd.Series(dtype=float)
    leverage = risk_results.get("leverage_risk", pd.Series(dtype=str)).fillna("Normal").astype(str) if not risk_results.empty else pd.Series(dtype=str)

    count = max(int(len(decisions)), 1)
    reduce_sell_ratio = float(decisions.isin(REDUCE_DECISIONS).sum() / count) if len(decisions) else 0.0
    buy_ratio = float(decisions.isin(BUY_DECISIONS).sum() / count) if len(decisions) else 0.0
    loss_ratio = float((return_rates < 0).sum() / len(return_rates)) if len(return_rates) else 0.0

    return {
        "average_final_score": float(final_scores.mean()) if not final_scores.empty else 45.0,
        "reduce_sell_ratio": reduce_sell_ratio,
        "buy_ratio": buy_ratio,
        "cash_ratio": cash_ratio,
        "concentration": concentration,
        "has_leverage_risk": bool(leverage.ne("Normal").any()) if len(leverage) else False,
        "loss_ratio": loss_ratio,
        "average_risk_penalty": float(penalties.mean()) if len(penalties) else 0.0,
        "holding_count": float(len(positions)),
    }


def calculate_overall_score(stats: dict[str, float | bool]) -> float:
    """Calculate overall portfolio score from score and risk statistics."""

    score = float(stats["average_final_score"])
    score -= float(stats["reduce_sell_ratio"]) * 20.0
    score += float(stats["buy_ratio"]) * 8.0
    if float(stats["cash_ratio"]) < 0.05:
        score -= 10.0
    elif float(stats["cash_ratio"]) < 0.10:
        score -= 6.0
    elif float(stats["cash_ratio"]) <= 0.20:
        score += 2.0
    if float(stats["concentration"]) >= 0.30:
        score -= 10.0
    elif float(stats["concentration"]) >= 0.20:
        score -= 5.0
    if bool(stats["has_leverage_risk"]):
        score -= 8.0
    score -= float(stats["loss_ratio"]) * 8.0
    return max(0.0, min(100.0, score))


def map_overall_decision(score: float, stats: dict[str, float | bool]) -> str:
    """Map portfolio summary score and risk mix to a decision label."""

    if float(stats["reduce_sell_ratio"]) >= 0.50 or score < 35:
        return "REDUCE"
    if score >= 70 and float(stats["buy_ratio"]) >= 0.30:
        return "BUY"
    return "HOLD"


def map_risk_level(stats: dict[str, float | bool]) -> str:
    """Map portfolio risk statistics to Low/Medium/High."""

    risk_points = 0
    if float(stats["reduce_sell_ratio"]) >= 0.30:
        risk_points += 2
    if float(stats["cash_ratio"]) < 0.10:
        risk_points += 1
    if float(stats["cash_ratio"]) < 0.05:
        risk_points += 1
    if float(stats["concentration"]) >= 0.30:
        risk_points += 2
    elif float(stats["concentration"]) >= 0.20:
        risk_points += 1
    if bool(stats["has_leverage_risk"]):
        risk_points += 2
    if float(stats["loss_ratio"]) >= 0.50:
        risk_points += 1
    if risk_points >= 4:
        return "High"
    if risk_points >= 2:
        return "Medium"
    return "Low"


def build_key_strengths(stats: dict[str, float | bool]) -> list[str]:
    """Build key portfolio strengths."""

    strengths: list[str] = []
    if float(stats["average_final_score"]) >= 65:
        strengths.append("\uc804\uccb4 \ud3c9\uade0 \uc810\uc218\uac00 \uc591\ud638\ud569\ub2c8\ub2e4.")
    if float(stats["buy_ratio"]) > 0:
        strengths.append("BUY \uc774\uc0c1 \ud310\ub2e8 \uc885\ubaa9\uc774 \ud3ec\ud568\ub418\uc5b4 \uc788\uc2b5\ub2c8\ub2e4.")
    if float(stats["reduce_sell_ratio"]) < 0.30:
        strengths.append("\uacfc\ub3c4\ud55c \ub9e4\ub3c4 \uc2e0\ud638\ub294 \ub9ce\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.")
    if float(stats["cash_ratio"]) >= 0.10:
        strengths.append("\uc77c\uc815 \uc218\uc900\uc758 \ud604\uae08 \uc5ec\ub825\uc774 \uc788\uc2b5\ub2c8\ub2e4.")
    return strengths or ["\ud604\uc7ac \ud3ec\ud2b8\ud3f4\ub9ac\uc624\ub294 \ubcf4\uc720 \uc0c1\ud0dc\ub97c \uc810\uac80\ud560 \uc218 \uc788\ub294 \uae30\ubcf8 \ub370\uc774\ud130\uac00 \uc788\uc2b5\ub2c8\ub2e4."]


def build_key_risks(stats: dict[str, float | bool]) -> list[str]:
    """Build key portfolio risks."""

    risks: list[str] = []
    if float(stats["concentration"]) >= 0.20:
        risks.append("\ud2b9\uc815 \uc885\ubaa9 \ube44\uc911\uc774 \ub192\uc2b5\ub2c8\ub2e4.")
    if float(stats["cash_ratio"]) < 0.10:
        risks.append("\ud604\uae08 \ube44\uc911\uc774 \ubd80\uc871\ud569\ub2c8\ub2e4.")
    if float(stats["reduce_sell_ratio"]) > 0:
        risks.append("REDUCE/SELL \ud310\ub2e8 \uc885\ubaa9\uc774 \ud3ec\ud568\ub418\uc5b4 \uc788\uc2b5\ub2c8\ub2e4.")
    if bool(stats["has_leverage_risk"]):
        risks.append("\ub808\ubc84\ub9ac\uc9c0 \uc0c1\ud488\uc774 \ud3ec\ud568\ub418\uc5b4 \uc788\uc2b5\ub2c8\ub2e4.")
    if float(stats["loss_ratio"]) >= 0.50:
        risks.append("\uc190\uc2e4 \uc885\ubaa9 \ube44\uc728\uc774 \ub192\uc2b5\ub2c8\ub2e4.")
    return risks or ["\ud604\uc7ac \uac15\ud55c \ub9ac\uc2a4\ud06c \uc2e0\ud638\ub294 \uc81c\ud55c\uc801\uc785\ub2c8\ub2e4."]


def build_action_items(stats: dict[str, float | bool], decision: str) -> list[str]:
    """Build portfolio-level action items."""

    actions: list[str] = []
    if decision == "BUY":
        actions.append("\uc2e0\uaddc \ub9e4\uc218\ub294 \ubd84\ud560\ub85c\ub9cc \uac80\ud1a0\ud558\uc138\uc694.")
    else:
        actions.append("\uc2e0\uaddc \ub9e4\uc218\ub294 \ubcf4\ub958\ud558\uace0 \ub9ac\uc2a4\ud06c\ub97c \uba3c\uc800 \uc810\uac80\ud558\uc138\uc694.")
    if float(stats["concentration"]) >= 0.20:
        actions.append("\ube44\uc911\uc774 \ub192\uc740 \uc885\ubaa9\uc744 \uba3c\uc800 \uc810\uac80\ud558\uc138\uc694.")
    if float(stats["reduce_sell_ratio"]) > 0:
        actions.append("REDUCE/SELL \uc885\ubaa9\uc740 \uc77c\ubd80 \ube44\uc911 \ucd95\uc18c\ub97c \uac80\ud1a0\ud558\uc138\uc694.")
    if float(stats["cash_ratio"]) < 0.10:
        actions.append("\ud604\uae08 \ube44\uc911\uc744 10~20%\uae4c\uc9c0 \ud655\ubcf4\ud558\ub294 \uac83\uc744 \uac80\ud1a0\ud558\uc138\uc694.")
    if bool(stats["has_leverage_risk"]):
        actions.append("\ub808\ubc84\ub9ac\uc9c0 \uc0c1\ud488\uc740 \ucd94\uac00 \ub9e4\uc218\ub97c \uc81c\ud55c\ud558\uc138\uc694.")
    return actions[:5]


def build_summary_text(decision: str, risk_level: str, stats: dict[str, float | bool]) -> str:
    """Build one concise portfolio summary paragraph."""

    if decision == "BUY":
        base = "\ud604\uc7ac \ud3ec\ud2b8\ud3f4\ub9ac\uc624\ub294 \uc804\uccb4 \uc810\uc218\uac00 \uc591\ud638\ud558\uace0 BUY \uc774\uc0c1 \uc885\ubaa9\uc774 \ud3ec\ud568\ub418\uc5b4 \uc788\uc5b4 \uc120\ubcc4\uc801 \ubd84\ud560\ub9e4\uc218\ub97c \uac80\ud1a0\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4."
    elif decision == "REDUCE":
        base = "\ud604\uc7ac \ud3ec\ud2b8\ud3f4\ub9ac\uc624\ub294 REDUCE/SELL \uc2e0\ud638\uc640 \ub9ac\uc2a4\ud06c\uac00 \ucee4 \uc77c\ubd80 \ube44\uc911 \ucd95\uc18c\ub97c \uba3c\uc800 \uac80\ud1a0\ud558\ub294 \uac83\uc774 \uc801\uc808\ud569\ub2c8\ub2e4."
    else:
        base = "\ud604\uc7ac \ud3ec\ud2b8\ud3f4\ub9ac\uc624\ub294 \uc804\uccb4\uc801\uc73c\ub85c \ubcf4\uc720 \uc720\uc9c0\uac00 \uc801\uc808\ud569\ub2c8\ub2e4."
    if risk_level in {"Medium", "High"}:
        base += " \ub2e4\ub9cc \ud2b9\uc815 \uc885\ubaa9 \ube44\uc911, \ud604\uae08 \ube44\uc911, \uc190\uc2e4 \uc885\ubaa9 \uc5ec\ubd80\ub97c \ud568\uaed8 \uc810\uac80\ud558\uc138\uc694."
    else:
        base += " \ud604\uc7ac \uac15\ud55c \ub9ac\uc2a4\ud06c \uc2e0\ud638\ub294 \uc81c\ud55c\uc801\uc774\uc9c0\ub9cc, \ucd94\uac00 \ub9e4\uc218\ub294 \ube44\uc911\uc744 \ud655\uc778\ud55c \ub4a4 \uc811\uadfc\ud558\uc138\uc694."
    return base


def calculate_summary_confidence(stats: dict[str, float | bool]) -> float:
    """Estimate confidence for portfolio summary based on data coverage."""

    confidence = 40.0
    if float(stats["holding_count"]) > 0:
        confidence += 20.0
    if float(stats["average_final_score"]) > 0:
        confidence += 20.0
    if float(stats["cash_ratio"]) >= 0:
        confidence += 10.0
    if float(stats["concentration"]) >= 0:
        confidence += 10.0
    return max(0.0, min(100.0, confidence))
