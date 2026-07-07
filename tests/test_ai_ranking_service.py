from __future__ import annotations

import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from modules.ai_judgement import AIJudgementSummary
from modules.analysis.analysis_models import TechnicalAnalysisResult
from modules.decision.decision_models import DecisionCode, DecisionResult
from modules.market.market_models import OHLCVDataResult, PriceData
from modules.ranking import ai_ranking_service as service


def make_analysis(ticker: str = "005930") -> TechnicalAnalysisResult:
    """Create a minimal successful technical analysis result."""

    return TechnicalAnalysisResult(
        ticker=ticker,
        latest_close=70000.0,
        rsi_14=55.0,
        ma20=69000.0,
        ma60=68000.0,
        ma120=65000.0,
        trend_status="상승추세",
        macd=1.0,
        macd_signal=0.5,
        macd_histogram=0.5,
        macd_status="상승 모멘텀",
        latest_volume=1000.0,
        avg_volume_20=900.0,
        volume_ratio=1.1,
        volume_status="거래량 보통",
        week52_high=80000.0,
        week52_low=50000.0,
        week52_position=65.0,
        success=True,
        message="OK",
    )


def make_decision(ticker: str = "005930", final_score: float = 77.0) -> DecisionResult:
    """Create a decision result whose final_score must become the AI score."""

    return DecisionResult(
        ticker=ticker,
        decision=DecisionCode.BUY,
        decision_score=final_score,
        risk_penalty=0.0,
        final_score=final_score,
        confidence_score=80.0,
        reasons=["공통 엔진 결과"],
        risk_messages=[],
        final_decision="BUY",
        score=final_score,
        confidence=80.0,
    )


def make_summary(score: float = 77.0) -> AIJudgementSummary:
    """Create a summary result for unified ranking tests."""

    return AIJudgementSummary(
        title="AI 판단",
        summary_text="summary",
        signal="BUY",
        score=score,
        confidence=80.0,
        positives=["좋은 점"],
        risks=["주의점"],
        strategy="분할 접근",
        action="살펴보기",
        one_line_conclusion="같은 엔진으로 계산한 결론입니다.",
        detailed_summary="상세 요약",
    )


def patch_unified_dependencies(monkeypatch, final_score: float = 77.0) -> None:
    """Patch provider dependencies so the service test is deterministic."""

    fixed_now = datetime(2026, 7, 8, 8, 30, tzinfo=ZoneInfo("Asia/Seoul"))
    data = pd.DataFrame(
        {
            "date": [pd.Timestamp(fixed_now)],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [1.0],
        }
    )
    monkeypatch.setattr(service, "now_datetime", lambda: fixed_now)
    monkeypatch.setattr(service, "get_current_price", lambda ticker, config, market_hint=None: PriceData(ticker, ticker, market_hint or "KOSPI", 1.0, "KRW", "test", True, "OK"))
    monkeypatch.setattr(service, "get_ohlcv", lambda request, config: OHLCVDataResult(request.ticker, request.ticker, request.market_hint or "KOSPI", data, "test", True, "OK"))
    monkeypatch.setattr(service, "analyze_ohlcv", lambda ticker, ohlcv: make_analysis(ticker))
    monkeypatch.setattr(service, "decide_one", lambda analysis: make_decision(str(analysis["ticker"]), final_score))
    monkeypatch.setattr(service, "build_ai_judgement_summary", lambda name, ticker, analysis, decision: make_summary(final_score))
    service.clear_ai_judgement_cache()


def test_unified_ai_score_uses_decision_final_score(monkeypatch) -> None:
    """AI score must be the same final_score used by the detail judgement."""

    patch_unified_dependencies(monkeypatch, final_score=82.5)
    result = service.get_unified_ai_judgement("삼성전자", "005930", "KOSPI")
    assert result.ai_score == 82.5
    assert result.final_signal == "BUY"
    assert result.one_line_summary == "같은 엔진으로 계산한 결론입니다."
    assert result.data_timestamp == "2026-07-08 08:30"
    assert result.is_decision_allowed is True


def test_build_ai_ranking_sorts_by_unified_ai_score(monkeypatch) -> None:
    """Ranking should sort by the shared AI score and cap visible rows at top 10."""

    candidates = [(f"종목{i}", f"T{i:02d}", "KOSPI") for i in range(12)]
    scores = {f"T{i:02d}": float(i) for i in range(12)}

    def fake_result(name: str, ticker: str, market: str):
        return service.UnifiedAIJudgementResult(
            ticker=ticker,
            name=name,
            market=market,
            ai_score=scores[ticker],
            final_signal="HOLD",
            signal_label="HOLD",
            one_line_summary="같은 엔진 결과",
            beginner_summary="요약",
            detail_summary="상세",
            updated_at="2026-07-08 09:00",
            data_timestamp="2026-07-08 09:00",
            source="test",
            success=True,
            is_fallback=False,
            error_message="",
        )

    monkeypatch.setattr(service, "select_candidate_pool", lambda market, candidate_limit=24: candidates)
    monkeypatch.setattr(service, "get_unified_ai_judgement", fake_result)
    ranking = service.build_ai_ranking("KOSPI", limit=10)

    assert len(ranking) == 10
    assert ranking.iloc[0]["ticker"] == "T11"
    assert ranking.iloc[0]["ai_score"] == 11.0
    assert ranking.iloc[-1]["ticker"] == "T02"
