from __future__ import annotations

from modules.ai_judgement import build_ai_judgement_summary


def test_ai_judgement_contains_required_beginner_sections():
    analysis = {
        "ticker": "005930",
        "trend_status": "상승추세",
        "macd_status": "상승 모멘텀",
        "volume_status": "거래량 보통",
        "rsi_14": 45,
        "week52_position": 50,
        "success": True,
    }
    decision = {"decision": "BUY", "final_decision": "BUY", "final_score": 72, "confidence_score": 82}

    summary = build_ai_judgement_summary("삼성전자", "005930", analysis, decision)

    assert "AI 투자 판단 요약" in summary.title
    assert summary.one_line_conclusion
    assert summary.detailed_summary
    assert summary.good_points
    assert summary.caution_points
    assert summary.uncertain_points
    assert summary.action_plan
    assert summary.beginner_explanation


def test_ai_judgement_handles_missing_name_and_ticker_safely():
    summary = build_ai_judgement_summary("", "", {}, {})

    assert "선택 종목" in summary.title
    assert "UNKNOWN" in summary.title
    assert summary.signal == "HOLD"
    assert summary.caution_points
    assert summary.uncertain_points


def test_buy_signal_still_includes_caution_points():
    summary = build_ai_judgement_summary("Apple", "AAPL", {"rsi_14": 55, "trend_status": "상승추세"}, {"final_decision": "BUY"})

    assert any("분할" in item or "비중" in item for item in summary.caution_points)


def test_reduce_signal_still_includes_good_points():
    summary = build_ai_judgement_summary(
        "Test",
        "TEST",
        {"rsi_14": 45, "trend_status": "중립", "macd_status": "중립", "volume_status": "거래량 보통"},
        {"final_decision": "REDUCE"},
    )

    assert summary.good_points
