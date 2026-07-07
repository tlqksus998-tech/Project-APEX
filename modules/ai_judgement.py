from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AIJudgementSummary:
    """Rule-based stock judgement summary."""

    title: str
    summary_text: str
    signal: str
    score: float
    confidence: float
    positives: list[str]
    risks: list[str]
    strategy: str
    action: str


def build_ai_judgement_summary(name: str, ticker: str, analysis: dict[str, object], decision: dict[str, object]) -> AIJudgementSummary:
    """Build a safe rule-based stock judgement summary without external AI APIs."""

    safe_name = str(name or "선택 종목").strip()
    safe_ticker = str(ticker or "UNKNOWN").strip()
    signal = str(decision.get("final_decision") or decision.get("decision") or "HOLD")
    score = safe_float(decision.get("final_score"), 45.0)
    confidence = safe_float(decision.get("confidence_score"), 50.0)
    trend = str(analysis.get("trend_status") or "데이터 부족")
    macd = str(analysis.get("macd_status") or "데이터 부족")
    volume = str(analysis.get("volume_status") or "데이터 부족")
    rsi = analysis.get("rsi_14")

    positives: list[str] = []
    risks: list[str] = []
    if "상승" in trend:
        positives.append("가격 추세가 상대적으로 양호합니다.")
    elif "하락" in trend:
        risks.append("단기 추세가 약해 보입니다.")
    else:
        risks.append("추세 판단을 더 확인할 필요가 있습니다.")

    if "상승" in macd:
        positives.append("MACD 모멘텀이 개선되고 있습니다.")
    elif "하락" in macd:
        risks.append("MACD 모멘텀이 약합니다.")

    if "증가" in volume or "보통" in volume:
        positives.append("거래량 흐름이 확인 가능한 수준입니다.")
    elif "감소" in volume:
        risks.append("거래량이 줄어 추세 신뢰도가 낮을 수 있습니다.")

    rsi_value = optional_float(rsi)
    if rsi_value is None:
        risks.append("RSI 데이터가 부족합니다.")
    elif rsi_value > 70:
        risks.append("RSI가 과열 구간에 가까워 추격 진입은 조심해야 합니다.")
    elif 30 <= rsi_value <= 60:
        positives.append("RSI가 비교적 안정 구간에 있습니다.")

    if not positives:
        positives.append("확인 가능한 긍정 요인이 아직 제한적입니다.")
    if not risks:
        risks.append("큰 위험 신호는 제한적이지만 비중 관리는 필요합니다.")

    action = recommended_action(signal)
    strategy = "바로 결론을 내리기보다 가격 지지, 거래량, 포트폴리오 비중을 함께 확인하세요."
    summary_text = f"{safe_name}({safe_ticker})의 현재 최종 판단은 {signal}입니다. 점수는 {score:.0f}점이며, 신규 진입보다 리스크와 비중을 함께 확인하는 접근이 적절합니다."
    return AIJudgementSummary(
        title=f"AI 투자판단 요약 - {safe_name} ({safe_ticker})",
        summary_text=summary_text,
        signal=signal,
        score=score,
        confidence=confidence,
        positives=positives[:3],
        risks=risks[:3],
        strategy=strategy,
        action=action,
    )


def recommended_action(signal: str) -> str:
    """Return a conservative action sentence for a decision signal."""

    mapping = {
        "STRONG_BUY": "관심 후보로 두고 분할 접근 가능성을 검토하세요.",
        "STRONG BUY": "관심 후보로 두고 분할 접근 가능성을 검토하세요.",
        "BUY APPROVED": "분할 접근으로 매수 검토가 가능합니다.",
        "BUY": "분할매수 관점으로 검토하되 현금비중을 먼저 확인하세요.",
        "WATCH": "관심 후보로 관찰하세요.",
        "WAIT": "지금 바로 신규매수하기보다 보류하세요.",
        "HOLD": "현재 비중을 유지하거나 관찰을 이어가세요.",
        "REDUCE": "일부 비중 축소 또는 리스크 점검을 검토하세요.",
        "SELL": "매도 또는 관찰리스트 전환을 검토하세요.",
        "DO NOT BUY": "신규매수는 피하고 리스크 관리가 우선입니다.",
    }
    return mapping.get(str(signal), mapping["HOLD"])


def optional_float(value: object) -> float | None:
    """Convert optional numeric values to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_float(value: object, default: float) -> float:
    """Convert numeric values to float with default fallback."""

    parsed = optional_float(value)
    return default if parsed is None else parsed
