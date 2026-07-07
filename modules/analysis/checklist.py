from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChecklistItem:
    """One beginner judgement checklist item."""

    category: str
    status: str
    description: str


@dataclass(frozen=True)
class AnalysisChecklist:
    """Beginner-friendly stock judgement checklist."""

    ticker: str
    items: list[ChecklistItem]
    summary: str


def build_analysis_checklist(analysis: dict[str, object], decision: dict[str, object] | None = None) -> AnalysisChecklist:
    """Build a balanced checklist from analysis and decision data."""

    decision = decision or {}
    ticker = str(analysis.get("ticker") or decision.get("ticker") or "UNKNOWN")
    items = [
        build_trend_item(str(analysis.get("trend_status") or "")),
        build_momentum_item(str(analysis.get("macd_status") or ""), as_optional_float(analysis.get("rsi_14"))),
        build_volume_item(str(analysis.get("volume_status") or "")),
        build_price_position_item(as_optional_float(analysis.get("week52_position"))),
        build_risk_item(str(decision.get("final_decision") or decision.get("decision") or "HOLD")),
        build_portfolio_fit_item(as_optional_float(decision.get("portfolio_fit_score"))),
        build_market_item(str(decision.get("market_regime") or "NEUTRAL")),
    ]
    summary = build_checklist_summary(items)
    return AnalysisChecklist(ticker=ticker, items=items, summary=summary)


def build_trend_item(status: str) -> ChecklistItem:
    """Build trend checklist item."""

    if "상승" in status:
        return ChecklistItem("추세", "좋음", "가격 흐름이 비교적 양호합니다.")
    if "하락" in status:
        return ChecklistItem("추세", "주의", "가격 흐름이 약해 추가 확인이 필요합니다.")
    if "부족" in status:
        return ChecklistItem("추세", "데이터 부족", "추세를 판단할 데이터가 충분하지 않습니다.")
    return ChecklistItem("추세", "보통", "추세가 한쪽으로 강하게 기울지는 않았습니다.")


def build_momentum_item(macd_status: str, rsi: float | None) -> ChecklistItem:
    """Build momentum checklist item."""

    if "하락" in macd_status or (rsi is not None and rsi > 70):
        return ChecklistItem("단기 흐름", "주의", "단기 흐름이 약하거나 과열되어 바로 진입은 조심해야 합니다.")
    if "상승" in macd_status and rsi is not None and 30 <= rsi <= 65:
        return ChecklistItem("단기 흐름", "좋음", "단기 흐름이 개선되는 모습이 있습니다.")
    if rsi is None:
        return ChecklistItem("단기 흐름", "데이터 부족", "RSI 데이터가 부족합니다.")
    return ChecklistItem("단기 흐름", "보통", "단기 흐름은 중립적으로 볼 수 있습니다.")


def build_volume_item(status: str) -> ChecklistItem:
    """Build volume checklist item."""

    if "증가" in status:
        return ChecklistItem("거래량", "좋음", "관심이 늘어나는 흐름이 보입니다.")
    if "감소" in status:
        return ChecklistItem("거래량", "주의", "거래량이 줄어 신호 신뢰도가 낮아질 수 있습니다.")
    if "부족" in status:
        return ChecklistItem("거래량", "데이터 부족", "거래량 데이터가 충분하지 않습니다.")
    return ChecklistItem("거래량", "보통", "거래량은 보통 수준입니다.")


def build_price_position_item(position: float | None) -> ChecklistItem:
    """Build 52-week price position item."""

    if position is None:
        return ChecklistItem("가격 위치", "데이터 부족", "52주 위치 데이터가 부족합니다.")
    if position > 80:
        return ChecklistItem("가격 위치", "주의", "최근 1년 기준 높은 위치라 추격매수는 조심해야 합니다.")
    if position < 20:
        return ChecklistItem("가격 위치", "보통", "낮은 위치지만 하락 이유를 함께 확인해야 합니다.")
    return ChecklistItem("가격 위치", "중립", "최근 1년 범위에서 중간권에 있습니다.")


def build_risk_item(signal: str) -> ChecklistItem:
    """Build risk checklist item."""

    value = signal.upper()
    if value in {"SELL", "REDUCE", "DO NOT BUY"}:
        return ChecklistItem("위험도", "주의", "리스크 관리가 먼저 필요한 판단입니다.")
    if value in {"WAIT", "WATCH", "HOLD"}:
        return ChecklistItem("위험도", "보통", "바로 크게 움직이기보다 관찰이 필요한 판단입니다.")
    return ChecklistItem("위험도", "보통", "매수 검토가 가능해도 비중 관리는 필요합니다.")


def build_portfolio_fit_item(score: float | None) -> ChecklistItem:
    """Build portfolio fit checklist item."""

    if score is None:
        return ChecklistItem("포트폴리오 적합도", "데이터 부족", "보유 비중 정보가 없어 종목 자체 흐름 중심으로 봅니다.")
    if score < 50:
        return ChecklistItem("포트폴리오 적합도", "주의", "내 포트폴리오 기준으로 추가 진입 부담이 큽니다.")
    if score < 70:
        return ChecklistItem("포트폴리오 적합도", "보통", "비중과 현금 여력을 먼저 확인해야 합니다.")
    return ChecklistItem("포트폴리오 적합도", "좋음", "포트폴리오 부담은 상대적으로 낮은 편입니다.")


def build_market_item(regime: str) -> ChecklistItem:
    """Build market regime checklist item."""

    value = regime.upper()
    if value in {"RISK", "STRONG_RISK"}:
        return ChecklistItem("시장 분위기", "주의", "시장 분위기가 불안정해 신규 진입은 보수적으로 봅니다.")
    if value in {"FAVORABLE", "STRONG_FAVORABLE"}:
        return ChecklistItem("시장 분위기", "좋음", "시장 분위기는 비교적 우호적입니다.")
    return ChecklistItem("시장 분위기", "관망", "시장 분위기는 중립으로 보고 확인이 필요합니다.")


def build_checklist_summary(items: list[ChecklistItem]) -> str:
    """Return one easy summary sentence."""

    caution_count = sum(1 for item in items if item.status in {"주의", "데이터 부족"})
    good_count = sum(1 for item in items if item.status == "좋음")
    if caution_count >= 3:
        return "확인할 위험 신호가 여러 개 있어 바로 매수하기보다 관찰이 먼저입니다."
    if good_count >= 3 and caution_count <= 1:
        return "좋은 신호가 몇 가지 있지만, 최종 결정 전 비중과 현금 여력을 확인하세요."
    return "기술적 조건은 일부 확인되지만 매수 확신을 줄 만큼 강한 상태는 아닙니다."


def as_optional_float(value: object) -> float | None:
    """Convert value to optional float."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return None if numeric != numeric else numeric
