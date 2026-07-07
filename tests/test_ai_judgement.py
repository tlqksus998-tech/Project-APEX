from __future__ import annotations

from modules.ai_judgement import build_ai_judgement_summary


def test_ai_judgement_summary_creation():
    analysis = {
        "trend_status": "상승추세",
        "macd_status": "상승 모멘텀",
        "volume_status": "거래량 보통",
        "rsi_14": 45,
    }
    decision = {"decision": "BUY", "final_score": 72, "confidence_score": 80}
    summary = build_ai_judgement_summary("삼성전자", "005930", analysis, decision)
    assert "삼성전자" in summary.title
    assert summary.summary_text
    assert summary.signal == "BUY"


def test_ai_judgement_handles_missing_name_and_ticker():
    summary = build_ai_judgement_summary("", "", {}, {})
    assert summary.summary_text
    assert summary.signal == "HOLD"
    assert summary.score >= 0
