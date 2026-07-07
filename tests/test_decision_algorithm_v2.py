from __future__ import annotations

from modules.analysis.analysis_engine import MACD_UP, TREND_UP, VOLUME_NORMAL
from modules.decision.decision_engine import decide_one


def strong_analysis(**overrides):
    data = {
        "ticker": "AAPL",
        "latest_close": 150.0,
        "rsi_14": 55.0,
        "ma20": 140.0,
        "ma60": 130.0,
        "ma120": 120.0,
        "trend_status": TREND_UP,
        "macd_status": MACD_UP,
        "volume_status": VOLUME_NORMAL,
        "week52_position": 55.0,
    }
    data.update(overrides)
    return data


def clean_risk(**overrides):
    data = {
        "ticker": "AAPL",
        "cash_risk": "Normal",
        "concentration_risk": "Normal",
        "averaging_down_risk": "Normal",
        "leverage_risk": "Normal",
        "total_risk_penalty": 0.0,
        "risk_messages": [],
    }
    data.update(overrides)
    return data


def test_score_is_bounded_and_market_defaults_neutral():
    result = decide_one(strong_analysis(), clean_risk())
    assert 0 <= result.score <= 100
    assert result.market_regime == "NEUTRAL"


def test_v2_fields_are_created():
    result = decide_one(strong_analysis(), clean_risk(), market_regime="FAVORABLE")
    assert result.stock_signal in {"STRONG BUY", "BUY", "WATCH", "HOLD", "REDUCE", "SELL"}
    assert result.final_decision in {"BUY APPROVED", "BUY", "WATCH", "WAIT", "HOLD", "REDUCE", "SELL", "DO NOT BUY"}
    assert result.beginner_summary
    assert result.advanced_summary


def test_favorable_clean_setup_can_be_buy_approved_or_buy():
    result = decide_one(strong_analysis(), clean_risk(), market_regime="FAVORABLE")
    assert result.final_decision in {"BUY APPROVED", "BUY", "WATCH"}
    assert result.stock_score >= 70
