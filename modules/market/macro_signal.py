from __future__ import annotations

from modules.market.macro_models import MacroIndicator

VALID_MARKET_SIGNALS = {"STRONG_RISK", "RISK", "NEUTRAL", "FAVORABLE", "STRONG_FAVORABLE"}
SIGNAL_LABELS = {
    "STRONG_RISK": "🔴 리스크 확대",
    "RISK": "🟠 주의",
    "NEUTRAL": "🟡 관망",
    "FAVORABLE": "🟢 우호적",
    "STRONG_FAVORABLE": "🟢 강한 우호",
}
SIGNAL_MESSAGES = {
    "STRONG_RISK": "변동성이 큰 구간입니다. 신규매수보다 방어와 현금 관리가 우선입니다.",
    "RISK": "주의가 필요한 시장입니다. 비중 확대는 천천히 검토하세요.",
    "NEUTRAL": "시장 방향성이 뚜렷하지 않습니다. 포트폴리오 리스크를 함께 확인하세요.",
    "FAVORABLE": "위험자산에 비교적 우호적인 흐름입니다. 다만 분할 접근이 적절합니다.",
    "STRONG_FAVORABLE": "시장 흐름이 강하게 우호적입니다. 과열 여부와 비중을 함께 점검하세요.",
}


def calculate_apex_macro_score(indicators: list[MacroIndicator]) -> float:
    """Calculate APEX Macro Score from rule-based macro signals."""

    if not indicators:
        return 50.0
    by_name = {item.name: item for item in indicators}
    score = 50.0

    score += equity_score(by_name.get("S&P500"), weight=9)
    score += equity_score(by_name.get("NASDAQ"), weight=9)
    score += equity_score(by_name.get("KOSPI"), weight=7)
    score += equity_score(by_name.get("KOSDAQ"), weight=5)
    score += inverse_score(by_name.get("VIX"), calm_bonus=8, shock_penalty=14)
    score += inverse_score(by_name.get("USD/KRW"), calm_bonus=5, shock_penalty=10)
    score += commodity_score(by_name.get("Gold"), spike_penalty=5)
    score += commodity_score(by_name.get("WTI"), spike_penalty=6)

    return max(0.0, min(100.0, score))


def classify_market_signal(score: float) -> tuple[str, str, str]:
    """Map macro score to signal code, label, and user-facing message."""

    if score >= 75:
        signal = "STRONG_FAVORABLE"
    elif score >= 60:
        signal = "FAVORABLE"
    elif score >= 45:
        signal = "NEUTRAL"
    elif score >= 30:
        signal = "RISK"
    else:
        signal = "STRONG_RISK"
    return signal, SIGNAL_LABELS[signal], SIGNAL_MESSAGES[signal]


def equity_score(indicator: MacroIndicator | None, weight: float) -> float:
    """Score equity index movement."""

    if indicator is None or indicator.status != "OK":
        return 0.0
    change = indicator.change_pct
    if change >= 0.01:
        return weight
    if change > 0:
        return weight * 0.55
    if change <= -0.015:
        return -weight
    return -weight * 0.45


def inverse_score(indicator: MacroIndicator | None, calm_bonus: float, shock_penalty: float) -> float:
    """Score indicators where falling is favorable, such as VIX or USD/KRW."""

    if indicator is None or indicator.status != "OK":
        return 0.0
    change = indicator.change_pct
    if change <= -0.01:
        return calm_bonus
    if change < 0:
        return calm_bonus * 0.5
    if change >= 0.02:
        return -shock_penalty
    return -shock_penalty * 0.35


def commodity_score(indicator: MacroIndicator | None, spike_penalty: float) -> float:
    """Score commodity spike risk."""

    if indicator is None or indicator.status != "OK":
        return 0.0
    change = indicator.change_pct
    if change >= 0.02:
        return -spike_penalty
    if change <= -0.01:
        return 2.0
    return 1.0
