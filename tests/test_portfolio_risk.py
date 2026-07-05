import pandas as pd

from modules.risk.portfolio_risk import evaluate_portfolio_risk


def make_positions(**overrides):
    row = {
        "ticker": "AAPL",
        "name": "Apple",
        "current_value": 1000.0,
        "weight": 0.10,
        "return_rate": 0.0,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_concentration_penalty_for_weight_above_30_percent():
    risk = evaluate_portfolio_risk(make_positions(weight=0.35), cash_amount=1000.0)

    assert risk.iloc[0]["concentration_risk"] == "High Concentration Risk"
    assert risk.iloc[0]["total_risk_penalty"] <= -20


def test_cash_penalty_for_cash_ratio_below_5_percent():
    risk = evaluate_portfolio_risk(make_positions(current_value=1000.0, weight=0.05), cash_amount=0.0)

    assert risk.iloc[0]["cash_risk"] == "High Cash Risk"
    assert risk.iloc[0]["total_risk_penalty"] <= -15


def test_averaging_down_penalty_for_loss_below_15_percent():
    risk = evaluate_portfolio_risk(make_positions(return_rate=-0.20), cash_amount=1000.0)

    assert risk.iloc[0]["averaging_down_risk"] == "High Averaging Down Risk"
    assert risk.iloc[0]["total_risk_penalty"] <= -15


def test_leverage_keyword_penalty():
    risk = evaluate_portfolio_risk(make_positions(ticker="TQQQ", name="TQQQ ETF"), cash_amount=1000.0)

    assert risk.iloc[0]["leverage_risk"] == "Leverage Risk"
    assert risk.iloc[0]["total_risk_penalty"] <= -15


def test_total_risk_penalty_is_never_positive():
    risk = evaluate_portfolio_risk(make_positions(weight=0.01, return_rate=0.05), cash_amount=10000.0)

    assert risk.iloc[0]["total_risk_penalty"] <= 0
