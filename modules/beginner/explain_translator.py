from __future__ import annotations


def decision_to_easy_label(signal: object) -> str:
    """Translate internal decision labels to simple Korean."""

    value = str(signal or "HOLD").upper().replace(" ", "_")
    if value in {"STRONG_BUY", "BUY_APPROVED"}:
        return "지금 관심 있게 볼 만해요"
    if value == "BUY":
        return "조금씩 살펴볼 만해요"
    if value in {"HOLD", "WATCH", "WAIT"}:
        return "지금은 지켜봐도 괜찮아요"
    if value == "REDUCE":
        return "조금 줄여도 괜찮아 보여요"
    if value in {"SELL", "DO_NOT_BUY"}:
        return "정리를 생각해볼 때예요"
    return "지금은 지켜봐도 괜찮아요"


def describe_price_position(position: float | None) -> str:
    """Describe 52-week price position without jargon."""

    if position is None:
        return "가격 위치를 아직 판단하기 어려워요"
    if position < 30:
        return "최근 기준으로 낮은 편이에요"
    if position <= 70:
        return "아직 너무 비싸 보이지는 않아요"
    return "이미 많이 오른 자리라 비쌀 수 있어요"


def describe_trend(trend_status: object, macd_status: object = "") -> str:
    """Describe trend in simple Korean."""

    trend = str(trend_status or "")
    macd = str(macd_status or "")
    if "상승" in trend or "상승" in macd:
        return "↗ 오르는 흐름이에요"
    if "하락" in trend or "하락" in macd:
        return "↘ 힘이 약해지고 있어요"
    return "→ 방향을 확인하는 중이에요"


def describe_interest(volume_status: object) -> str:
    """Describe volume as investor interest."""

    value = str(volume_status or "")
    if "증가" in value:
        return "평소보다 사람들이 더 많이 보고 있어요"
    if "감소" in value:
        return "관심이 조금 줄어든 모습이에요"
    if "부족" in value:
        return "관심도를 아직 판단하기 어려워요"
    return "평소와 비슷한 관심이에요"


def describe_risk(decision_label: object, rsi_value: float | None = None) -> str:
    """Describe risk in simple Korean."""

    value = str(decision_label or "").upper().replace(" ", "_")
    if value in {"SELL", "REDUCE", "DO_NOT_BUY"}:
        return "가격이 흔들릴 수 있어 조심해야 해요"
    if rsi_value is not None and rsi_value > 70:
        return "조금 뜨거워져서 조심해야 해요"
    return "조금 흔들릴 수 있어요"


def build_beginner_reasons(analysis: dict[str, object], decision: dict[str, object]) -> list[str]:
    """Build three easy positive reasons."""

    reasons: list[str] = []
    if "증가" in str(analysis.get("volume_status") or ""):
        reasons.append("사람들이 평소보다 더 관심을 보이고 있어요.")
    else:
        reasons.append("관심도를 확인하며 볼 만한 종목이에요.")
    if "상승" in str(analysis.get("trend_status") or "") or "상승" in str(analysis.get("macd_status") or ""):
        reasons.append("최근 주가 흐름이 나쁘지 않아요.")
    else:
        reasons.append("가격 방향을 차분히 확인할 수 있어요.")
    score = safe_float(decision.get("final_score") or decision.get("score"), 50.0)
    if score >= 70:
        reasons.append("APEX 점수가 비교적 좋은 편이에요.")
    else:
        reasons.append("아직 무리해서 보기보다 확인할 점이 남아 있어요.")
    return reasons[:3]


def build_beginner_warnings(analysis: dict[str, object], decision: dict[str, object]) -> list[str]:
    """Build two easy caution points."""

    warnings: list[str] = []
    rsi = optional_float(analysis.get("rsi_14"))
    if rsi is not None and rsi > 70:
        warnings.append("이미 많이 오른 뒤라면 잠깐 쉬어갈 수 있어요.")
    else:
        warnings.append("단기적으로 가격이 흔들릴 수 있어요.")
    if str(decision.get("final_decision") or decision.get("decision") or "").upper() in {"REDUCE", "SELL", "DO NOT BUY"}:
        warnings.append("새로 사기보다는 위험을 먼저 줄이는 게 좋아요.")
    else:
        warnings.append("시장 전체가 흔들리면 같이 떨어질 수 있어요.")
    return warnings[:2]


def optional_float(value: object) -> float | None:
    """Convert value to optional float."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return None if numeric != numeric else numeric


def safe_float(value: object, default: float) -> float:
    """Convert value to float with fallback."""

    numeric = optional_float(value)
    return default if numeric is None else numeric
