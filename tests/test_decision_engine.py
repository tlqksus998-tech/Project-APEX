import pandas as pd

from modules.analysis.analysis_engine import MACD_DOWN, MACD_UP, STATUS_INSUFFICIENT, STATUS_NEUTRAL, TREND_DOWN, TREND_UP, VOLUME_NORMAL
from modules.decision.decision_engine import decide_many, decide_one
from modules.decision.decision_models import DecisionCode


def base_analysis(**overrides):
    data = {
        "ticker": "AAPL",
        "rsi_14": 45.0,
        "trend_status": TREND_UP,
        "macd": 1.2,
        "macd_status": MACD_UP,
        "volume_ratio": 1.0,
        "volume_status": VOLUME_NORMAL,
        "week52_position": 50.0,
    }
    data.update(overrides)
    return data


def base_risk(**overrides):
    data = {
        "ticker": "AAPL",
        "total_risk_penalty": 0.0,
        "risk_messages": [],
    }
    data.update(overrides)
    return data


def test_uptrend_stable_rsi_macd_up_is_buy_or_better():
    result = decide_one(base_analysis(), base_risk())

    assert result.decision in {DecisionCode.BUY, DecisionCode.STRONG_BUY}
    assert result.decision_score >= 70


def test_overheated_rsi_reduces_score():
    stable = decide_one(base_analysis(rsi_14=45.0), base_risk())
    overheated = decide_one(base_analysis(rsi_14=75.0), base_risk())

    assert overheated.decision_score < stable.decision_score


def test_downtrend_can_reduce_or_sell():
    result = decide_one(
        base_analysis(
            rsi_14=72.0,
            trend_status=TREND_DOWN,
            macd_status=MACD_DOWN,
            volume_status=STATUS_INSUFFICIENT,
            volume_ratio=None,
            week52_position=90.0,
        ),
        base_risk(total_risk_penalty=-15.0),
    )

    assert result.decision in {DecisionCode.REDUCE, DecisionCode.SELL}


def test_insufficient_data_returns_hold_centered_result():
    result = decide_one(
        base_analysis(
            rsi_14=None,
            trend_status=STATUS_INSUFFICIENT,
            macd=None,
            macd_status=STATUS_INSUFFICIENT,
            volume_ratio=None,
            volume_status=STATUS_INSUFFICIENT,
            week52_position=None,
        ),
        base_risk(),
    )

    assert result.decision == DecisionCode.HOLD
    assert result.decision_score == 45.0


def test_confidence_score_is_bounded():
    result = decide_one(base_analysis(trend_status=STATUS_NEUTRAL), base_risk())

    assert 0 <= result.confidence_score <= 100


def test_risk_penalty_lowers_final_score():
    clean = decide_one(base_analysis(), base_risk(total_risk_penalty=0.0))
    risky = decide_one(base_analysis(), base_risk(total_risk_penalty=-30.0, risk_messages=["Risk penalty"] ))

    assert risky.final_score < clean.final_score
    assert risky.risk_penalty == -30.0
    assert risky.risk_messages == ["Risk penalty"]


def test_decision_mapping_uses_final_score():
    result = decide_one(base_analysis(), base_risk(total_risk_penalty=-60.0))

    assert result.final_score < result.decision_score
    assert result.decision in {DecisionCode.REDUCE, DecisionCode.SELL}


def test_decide_many_merges_risk_by_ticker():
    analysis = pd.DataFrame([base_analysis()])
    risk = pd.DataFrame([base_risk(total_risk_penalty=-20.0, risk_messages=["Concentration"] )])
    result = decide_many(analysis, risk)

    assert result.iloc[0]["risk_penalty"] == -20.0
    assert result.iloc[0]["risk_messages"] == ["Concentration"]
