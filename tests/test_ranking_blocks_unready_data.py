from __future__ import annotations

from modules.ranking import ai_ranking_service as service
from modules.ranking.ai_ranking_service import UnifiedAIJudgementResult


def test_ranking_includes_ready_and_caution_only(monkeypatch) -> None:
    """Ranking should include READY/CAUTION and exclude BLOCKED."""

    candidates = [("READY", "READY", "NASDAQ"), ("CAUTION", "CAUTION", "NASDAQ"), ("BLOCKED", "BLOCKED", "NASDAQ")]

    def fake_result(name: str, ticker: str, market: str):
        allowed = ticker != "BLOCKED"
        return UnifiedAIJudgementResult(
            ticker=ticker,
            name=name,
            market=market,
            ai_score=80.0 if allowed else None,
            final_signal="HOLD" if allowed else "DATA_UNAVAILABLE",
            signal_label="HOLD",
            one_line_summary="ok",
            beginner_summary="",
            detail_summary="",
            updated_at="2026-07-08 10:00",
            data_timestamp="2026-07-08 09:55",
            source="yfinance" if allowed else "fallback",
            success=allowed,
            is_fallback=not allowed,
            error_message="",
            readiness_level=ticker,
            is_decision_allowed=allowed,
        )

    monkeypatch.setattr(service, "select_candidate_pool", lambda market, candidate_limit=24: candidates)
    monkeypatch.setattr(service, "get_unified_ai_judgement", fake_result)
    ranking = service.build_ai_ranking("NASDAQ", limit=10)

    assert ranking["ticker"].tolist() == ["CAUTION", "READY"]
