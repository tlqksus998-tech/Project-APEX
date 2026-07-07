from __future__ import annotations

from dataclasses import dataclass, field


DATA_INSUFFICIENT = "데이터 부족"


@dataclass(frozen=True)
class AIJudgementSummary:
    """Rule-based beginner-friendly stock judgement summary."""

    title: str
    summary_text: str
    signal: str
    score: float
    confidence: float
    positives: list[str]
    risks: list[str]
    strategy: str
    action: str
    one_line_conclusion: str = ""
    detailed_summary: str = ""
    good_points: list[str] = field(default_factory=list)
    caution_points: list[str] = field(default_factory=list)
    uncertain_points: list[str] = field(default_factory=list)
    action_plan: dict[str, str] = field(default_factory=dict)
    beginner_explanation: str = ""


def build_ai_judgement_summary(name: str, ticker: str, analysis: dict[str, object], decision: dict[str, object]) -> AIJudgementSummary:
    """Build a safe rule-based judgement summary without external AI APIs."""

    safe_name = str(name or "선택 종목").strip() or "선택 종목"
    safe_ticker = str(ticker or "UNKNOWN").strip() or "UNKNOWN"
    signal = normalize_signal(str(decision.get("final_decision") or decision.get("decision") or "HOLD"))
    score = clamp(safe_float(decision.get("final_score") or decision.get("score"), 45.0), 0.0, 100.0)
    confidence = clamp(safe_float(decision.get("confidence_score") or decision.get("confidence"), 50.0), 0.0, 100.0)

    trend = str(analysis.get("trend_status") or DATA_INSUFFICIENT)
    macd = str(analysis.get("macd_status") or DATA_INSUFFICIENT)
    volume = str(analysis.get("volume_status") or DATA_INSUFFICIENT)
    rsi_value = optional_float(analysis.get("rsi_14"))
    week52_position = optional_float(analysis.get("week52_position"))

    good_points = build_good_points(trend, macd, volume, rsi_value, week52_position)
    caution_points = build_caution_points(signal, trend, macd, volume, rsi_value, decision)
    uncertain_points = build_uncertain_points(analysis, decision)
    one_line = build_one_line_conclusion(signal, score)
    detailed = build_detailed_summary(safe_name, signal, trend, macd, volume, rsi_value)
    action_plan = build_action_plan(signal)
    beginner_explanation = build_beginner_explanation(safe_name, signal)
    action = action_plan.get("신규매수", "지금은 관찰이 적절합니다.")
    strategy = build_strategy(signal, confidence)
    summary_text = f"{safe_name}({safe_ticker})의 현재 판단은 {signal}입니다. {one_line}"

    return AIJudgementSummary(
        title=f"AI 투자 판단 요약 - {safe_name} ({safe_ticker})",
        summary_text=summary_text,
        signal=signal,
        score=score,
        confidence=confidence,
        positives=good_points[:4],
        risks=caution_points[:4],
        strategy=strategy,
        action=action,
        one_line_conclusion=one_line,
        detailed_summary=detailed,
        good_points=good_points[:4],
        caution_points=caution_points[:4],
        uncertain_points=uncertain_points[:4],
        action_plan=action_plan,
        beginner_explanation=beginner_explanation,
    )


def normalize_signal(signal: str) -> str:
    """Normalize decision labels while preserving supported product wording."""

    value = str(signal or "HOLD").strip().upper().replace(" ", "_")
    mapping = {
        "STRONG_BUY": "BUY",
        "BUY_APPROVED": "BUY APPROVED",
        "DO_NOT_BUY": "DO NOT BUY",
    }
    return mapping.get(value, value.replace("_", " ") if value == "STRONG_BUY" else value)


def build_good_points(trend: str, macd: str, volume: str, rsi: float | None, week52_position: float | None) -> list[str]:
    """Return balanced positive points for the current setup."""

    points: list[str] = []
    if "상승" in trend:
        points.append("추세가 완전히 무너진 상태는 아닙니다.")
    elif "중립" in trend:
        points.append("가격 흐름이 한쪽으로 과하게 쏠려 있지는 않습니다.")

    if "상승" in macd:
        points.append("단기 흐름이 개선되는 신호가 일부 보입니다.")
    elif "중립" in macd:
        points.append("단기 모멘텀이 과도하게 나쁘지는 않습니다.")

    if "증가" in volume or "보통" in volume:
        points.append("거래량이 판단에 참고할 수 있는 수준입니다.")

    if rsi is not None and 30 <= rsi <= 65:
        points.append("RSI가 과열도 과매도도 아닌 비교적 해석 가능한 구간입니다.")

    if week52_position is not None and 20 <= week52_position <= 80:
        points.append("52주 가격 범위 안에서 지나치게 높은 위치는 아닙니다.")

    return points or ["확인 가능한 긍정 요인은 아직 제한적입니다."]


def build_caution_points(signal: str, trend: str, macd: str, volume: str, rsi: float | None, decision: dict[str, object]) -> list[str]:
    """Return caution points that must always be shown."""

    points: list[str] = []
    if signal in {"BUY", "BUY APPROVED"}:
        points.append("매수 검토가 가능하더라도 한 번에 크게 진입하기보다 분할 접근이 적절합니다.")
    if "하락" in trend:
        points.append("추세가 약해 바로 진입하기 전 추가 확인이 필요합니다.")
    if "하락" in macd:
        points.append("단기 흐름이 약해지고 있어 성급한 매수는 피하는 편이 좋습니다.")
    if "감소" in volume:
        points.append("거래량이 줄어 신호의 신뢰도가 낮아질 수 있습니다.")
    if rsi is None:
        points.append("RSI 데이터가 부족해 판단 신뢰도가 낮아질 수 있습니다.")
    elif rsi > 70:
        points.append("RSI가 과열 구간에 가까워 단기 추격매수는 조심해야 합니다.")
    elif rsi < 30:
        points.append("RSI가 과매도 구간이지만, 하락 중인 종목은 추가 하락 위험도 함께 봐야 합니다.")

    warnings = decision.get("warnings")
    if isinstance(warnings, list):
        points.extend(str(item) for item in warnings[:2] if str(item).strip())
    if not points:
        points.append("뚜렷한 위험 신호가 적어도 비중과 현금 여력은 반드시 확인하세요.")
    return points


def build_uncertain_points(analysis: dict[str, object], decision: dict[str, object]) -> list[str]:
    """Return uncertainty notes so the judgement stays balanced."""

    points = [
        "뉴스, 실적 발표, 공시 같은 외부 정보는 별도로 확인해야 합니다.",
        "시장 전체 분위기에 따라 같은 종목의 흐름도 달라질 수 있습니다.",
    ]
    if not analysis.get("success", True):
        points.append("일부 가격 데이터가 부족해 판단 정확도가 낮아질 수 있습니다.")
    if safe_float(decision.get("confidence_score") or decision.get("confidence"), 50.0) < 50:
        points.append("신뢰도가 높지 않아 결론보다 확인 항목을 우선해서 보세요.")
    return points


def build_one_line_conclusion(signal: str, score: float) -> str:
    """Return a single beginner-readable conclusion."""

    if signal in {"BUY APPROVED", "BUY"}:
        return "흐름은 나쁘지 않지만, 바로 크게 사기보다 분할 매수 검토가 적절합니다."
    if signal == "WATCH":
        return "관심 종목으로 지켜볼 만하지만 아직 확인할 조건이 남아 있습니다."
    if signal == "WAIT":
        return "좋아 보이는 부분이 있어도 지금은 기다리며 확인하는 쪽이 더 안전합니다."
    if signal == "HOLD":
        return "현재는 보유하거나 관찰하면서 추가 신호를 기다리는 판단입니다."
    if signal == "REDUCE":
        return "리스크가 커지고 있어 일부 비중 축소를 검토할 수 있습니다."
    if signal in {"SELL", "DO NOT BUY"}:
        return "신규매수는 피하고 손실 확대 방지와 리스크 관리를 먼저 보세요."
    return f"점수는 {score:.0f}점으로, 결론보다 조건 확인이 중요합니다."


def build_detailed_summary(name: str, signal: str, trend: str, macd: str, volume: str, rsi: float | None) -> str:
    """Return a short paragraph summary for beginners."""

    rsi_sentence = "RSI 데이터는 아직 부족합니다."
    if rsi is not None:
        if rsi < 30:
            rsi_sentence = "RSI는 과매도 구간이라 반등 가능성과 추가 하락 위험을 함께 봐야 합니다."
        elif rsi < 40:
            rsi_sentence = "RSI는 반등 관찰 구간으로, 가격이 실제로 회복되는지 확인이 필요합니다."
        elif rsi <= 60:
            rsi_sentence = "RSI는 중립 구간이라 과열도 과매도도 아닌 상태입니다."
        elif rsi <= 70:
            rsi_sentence = "RSI는 강세 구간이지만 단기 과열로 넘어가는지 확인해야 합니다."
        else:
            rsi_sentence = "RSI는 과열 주의 구간이라 추격매수는 조심해야 합니다."

    return (
        f"{name}은 현재 {signal} 판단입니다. "
        f"추세는 '{trend}', 단기 모멘텀은 '{macd}', 거래량은 '{volume}' 상태로 해석됩니다. "
        f"{rsi_sentence} 이미 보유 중이라면 무리한 추가매수보다 기존 비중과 손실 가능성을 먼저 점검하세요."
    )


def build_action_plan(signal: str) -> dict[str, str]:
    """Return action guide by decision label."""

    if signal in {"BUY APPROVED", "BUY"}:
        return {
            "신규매수": "가능하더라도 분할 접근으로 검토하세요.",
            "보유자": "보유는 가능하지만 목표 비중을 먼저 정하세요.",
            "추가매수": "20일선 지지와 거래량 확인 후 검토하세요.",
            "비중축소/손절": "명확한 위험 신호가 커지면 일부 축소 기준을 미리 정하세요.",
        }
    if signal in {"WATCH", "WAIT", "HOLD"}:
        return {
            "신규매수": "지금은 보류하고 관찰이 적절합니다.",
            "보유자": "보유는 가능하지만 손실 확대 여부를 확인하세요.",
            "추가매수": "지지 확인 전까지 서두르지 않는 편이 좋습니다.",
            "비중축소/손절": "REDUCE 이상 위험 신호가 나오면 일부 축소를 검토하세요.",
        }
    return {
        "신규매수": "신규매수는 피하는 편이 좋습니다.",
        "보유자": "보유 비중과 손실 한도를 먼저 점검하세요.",
        "추가매수": "물타기성 추가매수는 보류하세요.",
        "비중축소/손절": "일부 비중 축소 또는 관찰리스트 전환을 검토하세요.",
    }


def build_beginner_explanation(name: str, signal: str) -> str:
    """Explain the judgement without technical jargon."""

    return (
        f"{name}은 지금 당장 사야 한다는 의미가 아니라, 현재 흐름과 위험을 함께 본 참고 판단입니다. "
        f"APEX의 결론은 {signal}이지만, 최종 결정 전에는 내 현금비중과 이미 보유한 종목 비중을 같이 확인하세요."
    )


def build_strategy(signal: str, confidence: float) -> str:
    """Return a conservative strategy sentence."""

    if confidence < 50:
        return "데이터 신뢰도가 높지 않으므로 결론보다 확인 항목을 먼저 보세요."
    if signal in {"BUY APPROVED", "BUY"}:
        return "가격 지지, 거래량, 포트폴리오 비중을 함께 확인한 뒤 분할 접근하세요."
    if signal in {"REDUCE", "SELL", "DO NOT BUY"}:
        return "추가매수보다 손실 관리와 비중 축소 기준을 먼저 정하세요."
    return "관찰을 이어가며 추세와 거래량이 개선되는지 확인하세요."


def optional_float(value: object) -> float | None:
    """Convert optional numeric values to float."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return None if numeric != numeric else numeric


def safe_float(value: object, default: float) -> float:
    """Convert numeric values to float with default fallback."""

    parsed = optional_float(value)
    return default if parsed is None else parsed


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a numeric value."""

    return max(minimum, min(maximum, value))
