from __future__ import annotations

from app.ui.portfolio_view import SearchResult
from app.ui import stock_analysis_view
from modules.ranking.ai_ranking_service import UnifiedAIJudgementResult
from tests.test_ai_ranking_service import make_analysis, make_decision, make_summary


def test_stock_detail_uses_unified_ai_judgement_result(monkeypatch) -> None:
    """Stock detail analysis should consume the same unified result used by ranking."""

    decision = make_decision("005930", 88.0)
    unified = UnifiedAIJudgementResult(
        ticker="005930",
        name="삼성전자",
        market="KOSPI",
        ai_score=88.0,
        final_signal="BUY",
        signal_label="BUY",
        one_line_summary="공통 결과",
        beginner_summary="요약",
        detail_summary="상세",
        updated_at="2026-07-08 09:00",
        data_timestamp="2026-07-08 09:00",
        source="test",
        success=True,
        is_fallback=False,
        error_message="",
        price=object(),
        ohlcv=object(),
        analysis=make_analysis("005930"),
        decision=decision,
        summary=make_summary(88.0),
    )
    monkeypatch.setattr(stock_analysis_view, "get_unified_ai_judgement", lambda name, ticker, market: unified)
    monkeypatch.setattr(stock_analysis_view, "build_analysis_checklist", lambda analysis, decision_dict: {"items": []})

    detail = stock_analysis_view.analyze_selected_stock(SearchResult("삼성전자", "005930", "KOSPI", "KRW"))

    assert detail["decision"].final_score == 88.0
    assert detail["unified"].ai_score == 88.0
    assert detail["summary"].score == 88.0
