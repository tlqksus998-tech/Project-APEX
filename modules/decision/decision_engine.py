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
from modules.decision.decision_models import DecisionCode, DecisionResult, FinalDecision, StockSignal
from modules.scoring.confidence import calculate_confidence_score
from modules.scoring.decision_reason import build_decision_reasons


VALID_MARKET_REGIMES = {"STRONG_RISK", "RISK", "NEUTRAL", "FAVORABLE", "STRONG_FAVORABLE"}


def decide_one(analysis: dict[str, object], risk: dict[str, object] | None = None, market_regime: str | None = None) -> DecisionResult:
    """Create one rule-based decision result from technical analysis and portfolio risk."""

    risk = risk or {}
    ticker = str(analysis.get("ticker") or risk.get("ticker") or "UNKNOWN")
    regime = normalize_market_regime(market_regime)
    reasons: list[str] = []
    warnings: list[str] = []

    trend_component, trend_reason = score_trend_v2(analysis)
    momentum_component, momentum_reason = score_momentum_v2(analysis)
    volume_component, volume_reason = score_volume_v2(analysis)
    week52_score, week52_reason = score_week52(as_optional_float(analysis.get("week52_position")))

    stock_score = clamp((trend_component * 0.35) + (momentum_component * 0.30) + (volume_component * 0.15) + ((50 + week52_score) * 0.20), 0.0, 100.0)
    reasons.extend(build_decision_reasons(analysis, risk))
    reasons.extend([trend_reason, momentum_reason, volume_reason, week52_reason])

    market_adjustment = market_score_adjustment(regime)
    decision_score = clamp(stock_score + market_adjustment, 0.0, 100.0)
    risk_penalty = min(as_optional_float(risk.get("total_risk_penalty")) or 0.0, 0.0)
    risk_score = calculate_risk_score(risk, analysis, regime)
    portfolio_fit_score, portfolio_warnings = calculate_portfolio_fit_score(risk)
    warnings.extend(portfolio_warnings)
    confidence_score = calculate_confidence_score(analysis)
    weighted_score = clamp((decision_score * 0.55) + (risk_score * 0.25) + (portfolio_fit_score * 0.20), 0.0, 100.0)
    risk_capped_score = clamp(decision_score + risk_penalty, 0.0, 100.0)
    final_score = min(weighted_score, risk_capped_score) if risk_penalty < 0 else weighted_score
    if confidence_score < 20:
        warnings.append("데이터가 부족해 공격적인 판단을 제한했습니다.")
        stock_score = min(stock_score, 45.0)
        decision_score = min(decision_score, 45.0)
        final_score = min(final_score, 45.0)
    stock_signal = map_stock_signal(stock_score)
    final_decision, override_warnings = map_final_decision(final_score, stock_signal, risk_score, portfolio_fit_score, regime, confidence_score, risk)
    warnings.extend(override_warnings)
    decision = map_legacy_decision(final_decision, final_score)
    risk_messages = risk.get("risk_messages") if isinstance(risk.get("risk_messages"), list) else []
    warnings.extend([str(message) for message in risk_messages])
    action_guide = build_action_guide(final_decision)
    beginner_summary = build_beginner_summary(final_decision, stock_signal)
    advanced_summary = build_advanced_summary(stock_score, trend_component, momentum_component, volume_component, risk_score, portfolio_fit_score, regime, warnings)
    return DecisionResult(
        ticker=ticker,
        decision=decision,
        decision_score=decision_score,
        risk_penalty=risk_penalty,
        final_score=final_score,
        confidence_score=confidence_score,
        reasons=reasons,
        risk_messages=risk_messages,
        stock_signal=stock_signal.value,
        final_decision=final_decision.value,
        action=action_guide,
        score=final_score,
        confidence=confidence_score,
        market_regime=regime,
        stock_score=stock_score,
        trend_score=trend_component,
        momentum_score=momentum_component,
        volume_score=volume_component,
        risk_score=risk_score,
        portfolio_fit_score=portfolio_fit_score,
        warnings=warnings,
        action_guide=action_guide,
        beginner_summary=beginner_summary,
        advanced_summary=advanced_summary,
    )


def decide_many(analysis_results: pd.DataFrame, risk_results: pd.DataFrame | None = None, market_regime: str | None = None) -> pd.DataFrame:
    """Create decision results for all rows in an analysis DataFrame."""

    columns = [
        "ticker",
        "decision",
        "decision_score",
        "risk_penalty",
        "final_score",
        "confidence_score",
        "reasons",
        "risk_messages",
        "stock_signal",
        "final_decision",
        "action",
        "score",
        "confidence",
        "market_regime",
        "stock_score",
        "trend_score",
        "momentum_score",
        "volume_score",
        "risk_score",
        "portfolio_fit_score",
        "warnings",
        "action_guide",
        "beginner_summary",
        "advanced_summary",
    ]
    if analysis_results.empty:
        return pd.DataFrame(columns=columns)

    risk_by_ticker = build_risk_lookup(risk_results)
    rows = []
    for record in analysis_results.to_dict(orient="records"):
        ticker = str(record.get("ticker") or "UNKNOWN")
        result = decide_one(record, risk_by_ticker.get(ticker, {}), market_regime=market_regime)
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
                "stock_signal": result.stock_signal,
                "final_decision": result.final_decision,
                "action": result.action,
                "score": result.score,
                "confidence": result.confidence,
                "market_regime": result.market_regime,
                "stock_score": result.stock_score,
                "trend_score": result.trend_score,
                "momentum_score": result.momentum_score,
                "volume_score": result.volume_score,
                "risk_score": result.risk_score,
                "portfolio_fit_score": result.portfolio_fit_score,
                "warnings": result.warnings or [],
                "action_guide": result.action_guide,
                "beginner_summary": result.beginner_summary,
                "advanced_summary": result.advanced_summary,
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


def score_trend_v2(analysis: dict[str, object]) -> tuple[float, str]:
    """Score trend from latest close and moving averages on a 0-100 scale."""

    close = as_optional_float(analysis.get("latest_close"))
    ma20 = as_optional_float(analysis.get("ma20"))
    ma60 = as_optional_float(analysis.get("ma60"))
    ma120 = as_optional_float(analysis.get("ma120"))
    status = str(analysis.get("trend_status") or STATUS_INSUFFICIENT)
    if close is None:
        if status == TREND_UP:
            return 75.0, "Trend status is upward."
        if status == TREND_DOWN:
            return 35.0, "Trend status is downward."
        if status == STATUS_NEUTRAL:
            return 55.0, "Trend status is neutral."
        return 45.0, "Trend data is insufficient."
    if ma20 is not None and ma60 is not None and ma120 is not None and close > ma20 > ma60 > ma120:
        return 90.0, "Price is above MA20, MA60, and MA120 in a strong uptrend."
    if ma20 is not None and close > ma20:
        return 72.0, "Price is above MA20, showing short-term strength."
    if ma120 is not None and close < ma120:
        return 25.0, "Price is below MA120, indicating weak long-term trend."
    if ma60 is not None and close < ma60:
        return 38.0, "Price is below MA60, requiring caution."
    if status == TREND_UP:
        return 75.0, "Trend status is upward."
    if status == TREND_DOWN:
        return 35.0, "Trend status is downward."
    return 55.0, "Trend status is neutral."


def score_momentum_v2(analysis: dict[str, object]) -> tuple[float, str]:
    """Score RSI and MACD momentum on a 0-100 scale."""

    rsi = as_optional_float(analysis.get("rsi_14"))
    macd_status = str(analysis.get("macd_status") or STATUS_INSUFFICIENT)
    score = 50.0
    reasons: list[str] = []
    if rsi is None:
        reasons.append("RSI data is insufficient.")
    elif 40 <= rsi <= 60:
        score += 12
        reasons.append(f"RSI is {rsi:.1f}, inside a stable range.")
    elif 30 <= rsi < 40:
        score += 6
        reasons.append(f"RSI is {rsi:.1f}, a rebound watch area.")
    elif 60 < rsi <= 70:
        score += 10
        reasons.append(f"RSI is {rsi:.1f}, showing strength.")
    elif rsi > 70:
        score -= 15
        reasons.append(f"RSI is {rsi:.1f}, short-term overheating risk.")
    else:
        score -= 3
        reasons.append(f"RSI is {rsi:.1f}, oversold but still risky.")

    if macd_status == MACD_UP:
        score += 18
        reasons.append("MACD shows upward momentum.")
    elif macd_status == MACD_DOWN:
        score -= 18
        reasons.append("MACD shows downward momentum.")
    elif macd_status == STATUS_NEUTRAL:
        score += 4
        reasons.append("MACD is neutral.")
    else:
        reasons.append("MACD data is insufficient.")
    return clamp(score, 0.0, 100.0), " ".join(reasons)


def score_volume_v2(analysis: dict[str, object]) -> tuple[float, str]:
    """Score volume on a 0-100 scale."""

    volume_status = str(analysis.get("volume_status") or STATUS_INSUFFICIENT)
    trend_status = str(analysis.get("trend_status") or STATUS_INSUFFICIENT)
    if volume_status == VOLUME_UP and trend_status == TREND_UP:
        return 78.0, "Volume is increasing with an upward trend."
    if volume_status == VOLUME_UP and trend_status == TREND_DOWN:
        return 32.0, "Volume is increasing while price trend is weak."
    if volume_status == VOLUME_NORMAL:
        return 58.0, "Volume is normal."
    if volume_status == VOLUME_DOWN:
        return 42.0, "Volume is decreasing, lowering signal reliability."
    return 50.0, "Volume data is insufficient."


def calculate_risk_score(risk: dict[str, object], analysis: dict[str, object], market_regime: str) -> float:
    """Calculate a 0-100 risk score where higher means safer."""

    score = 100.0 + (min(as_optional_float(risk.get("total_risk_penalty")) or 0.0, 0.0) * 2.0)
    if as_optional_float(analysis.get("rsi_14")) and (as_optional_float(analysis.get("rsi_14")) or 0) > 70:
        score -= 10
    if market_regime == "STRONG_RISK":
        score -= 25
    elif market_regime == "RISK":
        score -= 12
    return clamp(score, 0.0, 100.0)


def calculate_portfolio_fit_score(risk: dict[str, object]) -> tuple[float, list[str]]:
    """Calculate portfolio fit and warnings from risk fields."""

    score = 100.0
    warnings: list[str] = []
    cash_risk = str(risk.get("cash_risk") or "")
    concentration_risk = str(risk.get("concentration_risk") or "")
    averaging_risk = str(risk.get("averaging_down_risk") or "")
    leverage_risk = str(risk.get("leverage_risk") or "")
    if "High Cash" in cash_risk:
        score -= 45
        warnings.append("현금비중 부족으로 신규매수는 보류가 적절합니다.")
    elif "Medium Cash" in cash_risk:
        score -= 30
        warnings.append("현금비중이 낮아 분할 접근이 필요합니다.")
    elif "Low Cash" in cash_risk:
        score -= 15
        warnings.append("현금비중을 먼저 확인하세요.")
    if "High Concentration" in concentration_risk:
        score -= 45
        warnings.append("단일 종목 비중이 높아 추가매수 승인이 어렵습니다.")
    elif "Medium Concentration" in concentration_risk:
        score -= 25
        warnings.append("단일 종목 비중이 높습니다.")
    if "High Averaging" in averaging_risk:
        score -= 35
        warnings.append("손실 -15% 이하 구간에서는 물타기 위험이 큽니다.")
    elif "Medium Averaging" in averaging_risk:
        score -= 20
        warnings.append("손실 구간 추가매수는 보수적으로 판단하세요.")
    if "Leverage" in leverage_risk:
        score -= 40
        warnings.append("레버리지 상품은 BUY APPROVED 대상에서 제외합니다.")
    return clamp(score, 0.0, 100.0), warnings


def normalize_market_regime(market_regime: str | None) -> str:
    """Return a valid market regime with NEUTRAL fallback."""

    value = str(market_regime or "NEUTRAL").upper()
    return value if value in VALID_MARKET_REGIMES else "NEUTRAL"


def market_score_adjustment(market_regime: str) -> float:
    """Return score adjustment from market regime."""

    return {
        "STRONG_RISK": -18.0,
        "RISK": -8.0,
        "NEUTRAL": 0.0,
        "FAVORABLE": 5.0,
        "STRONG_FAVORABLE": 8.0,
    }.get(market_regime, 0.0)


def map_stock_signal(stock_score: float) -> StockSignal:
    """Map stock-only score to a stock signal."""

    if stock_score >= 82:
        return StockSignal.STRONG_BUY
    if stock_score >= 70:
        return StockSignal.BUY
    if stock_score >= 60:
        return StockSignal.WATCH
    if stock_score >= 45:
        return StockSignal.HOLD
    if stock_score >= 30:
        return StockSignal.REDUCE
    return StockSignal.SELL


def map_final_decision(
    final_score: float,
    stock_signal: StockSignal,
    risk_score: float,
    portfolio_fit_score: float,
    market_regime: str,
    confidence: float,
    risk: dict[str, object],
) -> tuple[FinalDecision, list[str]]:
    """Map score and override rules to final decision."""

    warnings: list[str] = []
    if final_score >= 80 and risk_score >= 70 and portfolio_fit_score >= 70 and market_regime not in {"RISK", "STRONG_RISK"}:
        decision = FinalDecision.BUY_APPROVED
    elif final_score >= 70 and risk_score >= 60:
        decision = FinalDecision.BUY
    elif final_score >= 60:
        decision = FinalDecision.WATCH
    elif final_score >= 45:
        decision = FinalDecision.HOLD
    elif final_score >= 30:
        decision = FinalDecision.REDUCE
    else:
        decision = FinalDecision.SELL

    buy_family = {FinalDecision.BUY_APPROVED, FinalDecision.BUY}
    if confidence < 40 and decision in buy_family:
        warnings.append("데이터가 부족해 과도한 BUY 판단을 제한했습니다.")
        decision = FinalDecision.WATCH
    if portfolio_fit_score < 50 and decision in buy_family:
        warnings.append("포트폴리오 적합도가 낮아 신규매수를 WAIT로 조정했습니다.")
        decision = FinalDecision.WAIT
    if portfolio_fit_score < 60 and stock_signal in {StockSignal.STRONG_BUY, StockSignal.BUY} and decision in {FinalDecision.WATCH, FinalDecision.HOLD}:
        warnings.append("종목 신호는 양호하지만 포트폴리오 조건 때문에 WAIT로 조정했습니다.")
        decision = FinalDecision.WAIT
    if risk_score < 45 and decision in buy_family:
        warnings.append("리스크 점수가 낮아 신규매수를 WAIT로 조정했습니다.")
        decision = FinalDecision.WAIT
    if str(risk.get("leverage_risk") or "") == "Leverage Risk" and decision == FinalDecision.BUY_APPROVED:
        warnings.append("레버리지 상품은 BUY APPROVED로 표시하지 않습니다.")
        decision = FinalDecision.BUY if market_regime not in {"RISK", "STRONG_RISK"} else FinalDecision.WATCH
    if "High Averaging" in str(risk.get("averaging_down_risk") or ""):
        warnings.append("손실 -15% 이하 구간에서는 추가매수 금지 경고가 적용됩니다.")
        if decision in buy_family:
            decision = FinalDecision.WAIT
    if market_regime == "STRONG_RISK" and decision in buy_family:
        warnings.append("시장 STRONG_RISK 구간에서는 신규매수를 제한합니다.")
        decision = FinalDecision.DO_NOT_BUY if risk_score < 50 else FinalDecision.WAIT
    elif market_regime == "RISK" and decision == FinalDecision.BUY_APPROVED:
        warnings.append("시장 RISK 구간에서는 BUY APPROVED를 제한합니다.")
        decision = FinalDecision.BUY
    return decision, warnings


def map_legacy_decision(final_decision: FinalDecision, final_score: float) -> DecisionCode:
    """Map expanded final decision back to legacy DecisionCode."""

    if final_decision in {FinalDecision.BUY_APPROVED, FinalDecision.BUY}:
        return DecisionCode.BUY if final_score < 85 else DecisionCode.STRONG_BUY
    if final_decision in {FinalDecision.WATCH, FinalDecision.WAIT, FinalDecision.HOLD}:
        return DecisionCode.HOLD
    if final_decision == FinalDecision.REDUCE:
        return DecisionCode.REDUCE
    return DecisionCode.SELL


def build_action_guide(final_decision: FinalDecision) -> str:
    """Return a plain action guide for final decision."""

    return {
        FinalDecision.BUY_APPROVED: "분할 접근으로 매수 검토가 가능합니다.",
        FinalDecision.BUY: "매수 검토는 가능하지만 비중과 현금비중을 먼저 확인하세요.",
        FinalDecision.WATCH: "관심 후보로 관찰하세요.",
        FinalDecision.WAIT: "지금 바로 신규매수하기보다 보류하세요.",
        FinalDecision.HOLD: "현재는 보유 또는 관찰이 적절합니다.",
        FinalDecision.REDUCE: "일부 비중 축소를 검토하세요.",
        FinalDecision.SELL: "매도 또는 관찰리스트 전환을 검토하세요.",
        FinalDecision.DO_NOT_BUY: "신규매수는 피하고 리스크 관리가 우선입니다.",
    }[final_decision]


def build_beginner_summary(final_decision: FinalDecision, stock_signal: StockSignal) -> str:
    """Return beginner-friendly summary."""

    if final_decision == FinalDecision.BUY_APPROVED:
        return "종목 흐름과 포트폴리오 여건이 비교적 양호합니다. 그래도 한 번에 사기보다 분할 접근이 좋습니다."
    if final_decision == FinalDecision.WAIT:
        return "종목 신호가 나쁘지 않아도 현금비중이나 포트폴리오 리스크를 고려하면 지금 바로 사기에는 이릅니다."
    if final_decision == FinalDecision.HOLD:
        return "현재는 보유 또는 관찰을 유지하며 추가 신호를 기다리는 편이 적절합니다."
    if final_decision == FinalDecision.REDUCE:
        return "위험 신호가 커지고 있어 추가매수보다 일부 비중 축소를 검토해야 합니다."
    if final_decision in {FinalDecision.SELL, FinalDecision.DO_NOT_BUY}:
        return "위험 신호가 강해 신규매수는 피하고 손실 확대 방지를 우선 검토하세요."
    return f"종목 자체 신호는 {stock_signal.value}이며, 최종 판단은 {final_decision.value}입니다."


def build_advanced_summary(
    stock_score: float,
    trend_score: float,
    momentum_score: float,
    volume_score: float,
    risk_score: float,
    portfolio_fit_score: float,
    market_regime: str,
    warnings: list[str],
) -> str:
    """Return advanced score breakdown summary."""

    override = " / ".join(warnings[:3]) if warnings else "No override rule applied."
    return (
        f"Stock Score {stock_score:.1f}, Trend {trend_score:.1f}, Momentum {momentum_score:.1f}, "
        f"Volume {volume_score:.1f}, Risk {risk_score:.1f}, Portfolio Fit {portfolio_fit_score:.1f}, "
        f"Market Regime {market_regime}. Overrides: {override}"
    )


def calculate_confidence(analysis: dict[str, object]) -> float:
    """Calculate confidence score based on available analysis fields."""

    return calculate_confidence_score(analysis)


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
