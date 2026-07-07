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
    mapping = {"STRONG_BUY": "BUY", "BUY_APPROVED": "BUY APPROVED", "DO_NOT_BUY": "DO NOT BUY"}
    return mapping.get(value, value.replace("_", " ") if value == "STRONG_BUY" else value)


def build_good_points(trend: str, macd: str, volume: str, rsi: float | None, week52_position: float | None) -> list[str]:
    """Return balanced positive points for the current setup."""

    points: list[str] = []
    if "상승" in trend:
        points.append("최근 주가 흐름이 나쁘지 않아요.")
    elif "중립" in trend:
        points.append("가격이 한쪽으로 크게 쏠려 있지는 않아요.")
    if "상승" in macd:
        points.append("오르는 힘이 조금씩 생기고 있어요.")
    elif "중립" in macd:
        points.append("단기 흐름이 과하게 나쁘지는 않아요.")
    if "증가" in volume or "보통" in volume:
        points.append("사람들의 관심을 어느 정도 확인할 수 있어요.")
    if rsi is not None and 30 <= rsi <= 65:
        points.append("아직 너무 많이 오른 상태는 아니에요.")
    if week52_position is not None and 20 <= week52_position <= 80:
        points.append("최근 1년 기준으로 아주 비싼 자리만은 아니에요.")
    return points or ["아직 뚜렷하게 좋은 신호는 많지 않아요."]


def build_caution_points(signal: str, trend: str, macd: str, volume: str, rsi: float | None, decision: dict[str, object]) -> list[str]:
    """Return caution points that must always be shown."""

    points: list[str] = []
    if signal in {"BUY", "BUY APPROVED"}:
        points.append("좋아 보여도 한 번에 크게 사기보다는 조금씩 보는 편이 좋아요.")
    if "하락" in trend:
        points.append("최근 흐름이 약해서 바로 사기 전 확인이 필요해요.")
    if "하락" in macd:
        points.append("오르는 힘이 약해지고 있어요.")
    if "감소" in volume:
        points.append("관심이 줄어들어 신호가 약할 수 있어요.")
    if rsi is None:
        points.append("일부 지표 데이터가 부족해요.")
    elif rsi > 70:
        points.append("조금 뜨거워졌어요. 급하게 사기보다는 조심해요.")
    elif rsi < 30:
        points.append("많이 내려온 상태지만 더 흔들릴 수도 있어요.")
    warnings = decision.get("warnings")
    if isinstance(warnings, list):
        points.extend(str(item) for item in warnings[:2] if str(item).strip())
    if not points:
        points.append("큰 위험 신호가 적어도 내 비중과 현금은 꼭 확인하세요.")
    return points


def build_uncertain_points(analysis: dict[str, object], decision: dict[str, object]) -> list[str]:
    """Return uncertainty notes so the judgement stays balanced."""

    points = ["뉴스와 실적은 따로 확인해야 해요.", "시장 전체가 흔들리면 좋은 종목도 같이 흔들릴 수 있어요."]
    if not analysis.get("success", True):
        points.append("일부 가격 데이터가 부족할 수 있어요.")
    if safe_float(decision.get("confidence_score") or decision.get("confidence"), 50.0) < 50:
        points.append("판단 신뢰도가 높지 않으니 결론보다 확인할 점을 먼저 보세요.")
    return points


def build_one_line_conclusion(signal: str, score: float) -> str:
    """Return a single beginner-readable conclusion."""

    if signal in {"BUY APPROVED", "BUY"}:
        return "흐름은 괜찮지만 조금씩 살펴보는 편이 좋아요."
    if signal == "WATCH":
        return "관심 있게 볼 만하지만 아직 더 확인할 점이 있어요."
    if signal == "WAIT":
        return "지금은 서두르지 말고 더 지켜보는 편이 좋아요."
    if signal == "HOLD":
        return "지금은 지켜봐도 괜찮아요."
    if signal == "REDUCE":
        return "위험이 커질 수 있어 조금 줄여도 괜찮아 보여요."
    if signal in {"SELL", "DO NOT BUY"}:
        return "새로 사기보다는 정리를 생각해볼 때예요."
    return f"점수는 {score:.0f}점이에요. 결론보다 확인할 점을 먼저 보세요."


def build_detailed_summary(name: str, signal: str, trend: str, macd: str, volume: str, rsi: float | None) -> str:
    """Return a short paragraph summary for beginners."""

    rsi_sentence = "RSI 데이터는 아직 부족해요."
    if rsi is not None:
        if rsi < 30:
            rsi_sentence = "많이 내려온 자리라 반등 가능성도 있지만 더 흔들릴 수도 있어요."
        elif rsi <= 60:
            rsi_sentence = "아직 너무 많이 오른 상태는 아니에요."
        elif rsi <= 70:
            rsi_sentence = "흐름은 강하지만 조금 뜨거워지는지 확인해야 해요."
        else:
            rsi_sentence = "조금 뜨거워졌어요. 급하게 사기보다는 조심해요."
    return f"{name}의 현재 판단은 {signal}입니다. 최근 흐름은 '{trend}', 관심도는 '{volume}'로 해석됩니다. {rsi_sentence}"


def build_action_plan(signal: str) -> dict[str, str]:
    """Return action guide by decision label."""

    if signal in {"BUY APPROVED", "BUY"}:
        return {"신규매수": "한 번에 많이 사지 말고 조금씩 보세요.", "보유자": "목표 비중을 먼저 정하세요.", "추가매수": "가격이 버티는지 확인한 뒤 보세요.", "정리": "위험 신호가 커지면 줄일 기준을 정하세요."}
    if signal in {"WATCH", "WAIT", "HOLD"}:
        return {"신규매수": "지금은 서두르지 않아도 괜찮아요.", "보유자": "보유하면서 흐름을 확인하세요.", "추가매수": "아직은 기다리는 편이 좋아요.", "정리": "위험 신호가 커지면 줄이는 것도 생각하세요."}
    return {"신규매수": "새로 사는 것은 피하는 편이 좋아요.", "보유자": "내 손실 한도를 먼저 확인하세요.", "추가매수": "물타기는 조심하세요.", "정리": "일부 정리도 검토하세요."}


def build_beginner_explanation(name: str, signal: str) -> str:
    """Explain the judgement without technical jargon."""

    return f"{name}을 지금 꼭 사야 한다는 뜻은 아니에요. APEX 판단은 {signal}이지만, 내 돈의 여유와 이미 가진 종목 비중을 같이 확인해야 해요."


def build_strategy(signal: str, confidence: float) -> str:
    """Return a conservative strategy sentence."""

    if confidence < 50:
        return "데이터가 부족하니 결론보다 확인할 점을 먼저 보세요."
    if signal in {"BUY APPROVED", "BUY"}:
        return "가격 흐름과 내 포트폴리오 비중을 확인한 뒤 조금씩 접근하세요."
    if signal in {"REDUCE", "SELL", "DO NOT BUY"}:
        return "추가매수보다 위험 관리가 먼저예요."
    return "흐름이 좋아지는지 조금 더 지켜보세요."


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
