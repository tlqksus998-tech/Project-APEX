from __future__ import annotations

from app.ui.design_system import render_metric_grid
from modules.portfolio_engine.models import PortfolioEngineSnapshot
from modules.summary.summary_models import PortfolioSummaryResult
from modules.utils import format_currency, format_percent


def render_kpi_summary(snapshot: PortfolioEngineSnapshot, scores: dict[str, float | str], macro_score: float, summary: PortfolioSummaryResult) -> None:
    """Render premium KPI summary cards."""

    decision = str(scores.get("decision", summary.overall_decision or "HOLD"))
    risk_level = summary.risk_level or "Medium"
    return_rate = 0.0
    if snapshot.total_invested_krw > 0:
        return_rate = (snapshot.total_current_value_krw - snapshot.total_invested_krw) / snapshot.total_invested_krw
    decision_tone = "positive" if decision in {"BUY", "STRONG_BUY"} else "warning" if decision == "REDUCE" else "negative" if decision == "SELL" else "neutral"
    risk_tone = "negative" if risk_level == "High" else "warning" if risk_level == "Medium" else "positive"
    cards = [
        ("총자산", format_currency(snapshot.total_assets_krw), "현금 포함 KRW 환산", "info"),
        ("총수익률", format_percent(return_rate), "KRW 환산 기준", "positive" if return_rate >= 0 else "negative"),
        ("총현금", format_currency(snapshot.total_cash_krw), f"현금비중 {format_percent(snapshot.cash_ratio)}", "neutral" if snapshot.cash_ratio < 0.1 else "positive"),
        ("APEX Macro Score", f"{macro_score:.1f}", "오늘 시장 온도", "positive" if macro_score >= 60 else "warning" if macro_score < 45 else "neutral"),
        ("오늘의 투자판단", decision, "포트폴리오 기준", decision_tone),
        ("Risk Level", risk_level, "리스크 관리 우선순위", risk_tone),
    ]
    render_metric_grid(cards, columns=3)
