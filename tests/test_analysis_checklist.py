from __future__ import annotations

from modules.analysis.checklist import build_analysis_checklist


def test_analysis_checklist_creation():
    checklist = build_analysis_checklist(
        {
            "ticker": "005930",
            "trend_status": "상승추세",
            "macd_status": "상승 모멘텀",
            "volume_status": "거래량 보통",
            "rsi_14": 45,
            "week52_position": 50,
        },
        {"final_decision": "WATCH", "portfolio_fit_score": 80, "market_regime": "NEUTRAL"},
    )

    assert checklist.ticker == "005930"
    assert len(checklist.items) == 7
    assert checklist.summary


def test_analysis_checklist_handles_missing_data():
    checklist = build_analysis_checklist({}, {})

    assert checklist.ticker == "UNKNOWN"
    assert len(checklist.items) == 7
    assert any(item.status == "데이터 부족" for item in checklist.items)
