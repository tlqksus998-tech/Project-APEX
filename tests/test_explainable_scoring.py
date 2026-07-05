import pandas as pd

from modules.scoring.confidence import calculate_confidence_score, portfolio_confidence
from modules.scoring.decision_reason import build_decision_reasons, build_portfolio_reason_summary
from modules.scoring.recommendation import build_recommendations


def test_confidence_score_uses_available_fields():
    analysis = {
        "rsi_14": 45.0,
        "trend_status": "\uc0c1\uc2b9\ucd94\uc138",
        "macd": 1.2,
        "macd_status": "\uc0c1\uc2b9 \ubaa8\uba58\ud140",
        "volume_ratio": 1.0,
        "volume_status": "\uac70\ub798\ub7c9 \ubcf4\ud1b5",
        "week52_position": 50.0,
    }

    assert calculate_confidence_score(analysis) == 100.0


def test_confidence_score_drops_when_data_missing():
    analysis = {
        "rsi_14": None,
        "trend_status": "\ub370\uc774\ud130 \ubd80\uc871",
        "macd": None,
        "macd_status": "\ub370\uc774\ud130 \ubd80\uc871",
        "volume_ratio": None,
        "volume_status": "\ub370\uc774\ud130 \ubd80\uc871",
        "week52_position": None,
    }

    assert calculate_confidence_score(analysis) == 0.0


def test_decision_reasons_include_indicator_and_risk_lines():
    reasons = build_decision_reasons(
        {
            "rsi_14": 45.0,
            "macd_status": "\uc0c1\uc2b9 \ubaa8\uba58\ud140",
            "volume_status": "\uac70\ub798\ub7c9 \uac10\uc18c",
            "trend_status": "\uc0c1\uc2b9\ucd94\uc138",
        },
        {"concentration_risk": "High Concentration Risk", "total_risk_penalty": -20.0},
    )

    assert any("RSI" in reason for reason in reasons)
    assert any("MACD" in reason for reason in reasons)
    assert any("\ube44\uc911" in reason for reason in reasons)


def test_recommendations_follow_decision():
    hold = build_recommendations("HOLD")
    sell = build_recommendations("SELL")

    assert any("\ubcf4\ub958" in item for item in hold)
    assert any("\uc190\uc808" in item for item in sell)


def test_portfolio_explanation_helpers():
    decisions = pd.DataFrame([{"confidence_score": 80.0}, {"confidence_score": 100.0}])
    analysis = pd.DataFrame(
        [
            {"rsi_14": 45.0, "macd_status": "\uc0c1\uc2b9 \ubaa8\uba58\ud140", "volume_status": "\uac70\ub798\ub7c9 \ubcf4\ud1b5", "trend_status": "\uc0c1\uc2b9\ucd94\uc138"}
        ]
    )
    risk = pd.DataFrame([{"total_risk_penalty": -20.0, "concentration_risk": "High Concentration Risk", "cash_risk": "Normal", "leverage_risk": "Normal"}])

    assert portfolio_confidence(decisions) == 90.0
    assert build_portfolio_reason_summary(analysis, risk)
