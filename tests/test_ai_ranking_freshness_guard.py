from __future__ import annotations

from modules.ranking.ai_ranking_service import UnifiedAIJudgementResult
from modules.ranking import ai_ranking_service as service


def test_ai_ranking_excludes_unallowed_results(monkeypatch) -> None:
    """AI ranking should exclude stale/fallback/unavailable judgement results."""

    candidates = [("정상", "OK", "KOSPI"), ("차단", "BAD", "KOSPI")]

    def fake_result(name: str, ticker: str, market: str):
        if ticker == "BAD":
            return UnifiedAIJudgementResult(
                ticker=ticker,
                name=name,
                market=market,
                ai_score=None,
                final_signal="DATA_UNAVAILABLE",
                signal_label="판단 보류",
                one_line_summary="데이터 부족",
                beginner_summary="",
                detail_summary="",
                updated_at="2026-07-08 10:00",
                data_timestamp="확인 불가",
                source="fallback",
                success=False,
                is_fallback=True,
                error_message="fallback",
                is_decision_allowed=False,
            )
        return UnifiedAIJudgementResult(
            ticker=ticker,
            name=name,
            market=market,
            ai_score=75.0,
            final_signal="BUY",
            signal_label="BUY",
            one_line_summary="정상 데이터",
            beginner_summary="",
            detail_summary="",
            updated_at="2026-07-08 10:00",
            data_timestamp="2026-07-08 09:55",
            source="pykrx",
            success=True,
            is_fallback=False,
            error_message="",
            is_decision_allowed=True,
        )

    monkeypatch.setattr(service, "select_candidate_pool", lambda market, candidate_limit=24: candidates)
    monkeypatch.setattr(service, "get_unified_ai_judgement", fake_result)

    ranking = service.build_ai_ranking("KOSPI", limit=10)

    assert ranking["ticker"].tolist() == ["OK"]
    assert int(ranking["excluded_count"].max()) == 1
