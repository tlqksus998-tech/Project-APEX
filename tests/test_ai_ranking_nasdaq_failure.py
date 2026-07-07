from __future__ import annotations

from modules.ranking import ai_ranking_service as service
from modules.ranking.ai_ranking_service import UnifiedAIJudgementResult


def make_result(ticker: str, allowed: bool = True, score: float | None = 70.0) -> UnifiedAIJudgementResult:
    """Build a ranking result for NASDAQ failure tests."""

    return UnifiedAIJudgementResult(
        ticker=ticker,
        name=ticker,
        market="NASDAQ",
        ai_score=score,
        final_signal="HOLD" if allowed else "DATA_UNAVAILABLE",
        signal_label="HOLD" if allowed else "판단 보류",
        one_line_summary="정상" if allowed else "데이터 부족",
        beginner_summary="",
        detail_summary="",
        updated_at="2026-07-08 10:00",
        data_timestamp="2026-07-08 09:55" if allowed else "확인 불가",
        source="yfinance" if allowed else "fallback",
        success=allowed,
        is_fallback=not allowed,
        error_message="" if allowed else "fallback",
        freshness_status="delayed" if allowed else "unknown",
        readiness_level="CAUTION" if allowed else "BLOCKED",
        is_decision_allowed=allowed,
    )


def test_nasdaq_default_candidates_include_required_symbols() -> None:
    """NASDAQ fallback candidate pool should contain representative tickers."""

    tickers = {ticker for _, ticker, _ in service.DEFAULT_NASDAQ_CANDIDATES}
    for ticker in ["AAPL", "MSFT", "NVDA", "TSLA", "AVGO", "AMD", "QQQ"]:
        assert ticker in tickers


def test_partial_nasdaq_failures_do_not_empty_entire_ranking(monkeypatch) -> None:
    """One failed ticker should be excluded while other successful tickers remain."""

    candidates = [("AAPL", "AAPL", "NASDAQ"), ("BAD", "BAD", "NASDAQ"), ("NVDA", "NVDA", "NASDAQ")]
    monkeypatch.setattr(service, "select_candidate_pool", lambda market, candidate_limit=24: candidates)
    monkeypatch.setattr(service, "get_unified_ai_judgement", lambda name, ticker, market: make_result(ticker, allowed=ticker != "BAD", score=80.0 if ticker == "NVDA" else 70.0))

    ranking = service.build_ai_ranking("NASDAQ", limit=10)

    assert ranking["ticker"].tolist() == ["NVDA", "AAPL"]
    assert int(ranking["excluded_count"].max()) == 1


def test_all_nasdaq_failures_return_empty_frame_not_exception(monkeypatch) -> None:
    """All failures should return an empty ranking frame safely."""

    candidates = [("BAD1", "BAD1", "NASDAQ"), ("BAD2", "BAD2", "NASDAQ")]
    monkeypatch.setattr(service, "select_candidate_pool", lambda market, candidate_limit=24: candidates)
    monkeypatch.setattr(service, "get_unified_ai_judgement", lambda name, ticker, market: make_result(ticker, allowed=False, score=None))

    ranking = service.build_ai_ranking("NASDAQ", limit=10)

    assert ranking.empty
    assert "excluded_count" in ranking.columns
