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


def test_low_cash_turns_buy_into_wait():
    result = decide_one(strong_analysis(), clean_risk(cash_risk="High Cash Risk", total_risk_penalty=-15.0))
    assert result.final_decision == "WAIT"
    assert any("현금비중" in warning for warning in (result.warnings or []))


def test_high_concentration_turns_buy_into_wait():
    result = decide_one(strong_analysis(), clean_risk(concentration_risk="High Concentration Risk", total_risk_penalty=-20.0))
    assert result.final_decision == "WAIT"


def test_leverage_cannot_be_buy_approved():
    result = decide_one(
        strong_analysis(ticker="TQQQ"),
        clean_risk(ticker="TQQQ", leverage_risk="Leverage Risk", total_risk_penalty=-15.0),
        market_regime="STRONG_FAVORABLE",
    )
    assert result.final_decision != "BUY APPROVED"


def test_large_loss_warning_created():
    result = decide_one(strong_analysis(), clean_risk(averaging_down_risk="High Averaging Down Risk", total_risk_penalty=-15.0))
    assert any("-15%" in warning for warning in (result.warnings or []))


def test_strong_risk_market_limits_buy_family():
    result = decide_one(strong_analysis(), clean_risk(), market_regime="STRONG_RISK")
    assert result.final_decision not in {"BUY APPROVED", "BUY"}


def test_insufficient_data_does_not_break_or_buy():
    result = decide_one({"ticker": "EMPTY"}, clean_risk())
    assert result.final_decision in {"HOLD", "WATCH", "WAIT"}
    assert result.beginner_summary
