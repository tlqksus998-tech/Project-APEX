import pandas as pd

from modules.summary import generate_portfolio_summary


def base_metrics(value: float = 1000.0):
    return {"total_invested": value, "total_current_value": value, "profit_loss": 0.0, "return_rate": 0.0}


def test_empty_portfolio_summary_is_safe():
    result = generate_portfolio_summary({}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), cash_amount=0)

    assert result.summary_text
    assert result.overall_decision == "HOLD"


def test_reduce_ratio_raises_risk_level():
    positions = pd.DataFrame(
        [
            {"ticker": "A", "weight": 0.4, "return_rate": -0.1},
            {"ticker": "B", "weight": 0.3, "return_rate": -0.2},
        ]
    )
    decisions = pd.DataFrame(
        [
            {"ticker": "A", "final_score": 30, "decision": "REDUCE"},
            {"ticker": "B", "final_score": 20, "decision": "SELL"},
        ]
    )
    risks = pd.DataFrame(
        [
            {"ticker": "A", "total_risk_penalty": -30, "leverage_risk": "Normal"},
            {"ticker": "B", "total_risk_penalty": -30, "leverage_risk": "Leverage Risk"},
        ]
    )

    result = generate_portfolio_summary(base_metrics(), positions, decisions, risks, cash_amount=0)

    assert result.risk_level == "High"
    assert result.overall_decision == "REDUCE"


def test_low_cash_adds_cash_action_item():
    positions = pd.DataFrame([{"ticker": "A", "weight": 0.1, "return_rate": 0.02}])
    decisions = pd.DataFrame([{"ticker": "A", "final_score": 60, "decision": "HOLD"}])
    risks = pd.DataFrame([{"ticker": "A", "total_risk_penalty": -10, "leverage_risk": "Normal"}])

    result = generate_portfolio_summary(base_metrics(), positions, decisions, risks, cash_amount=0)

    assert any("10~20%" in item for item in result.action_items)


def test_high_average_score_raises_overall_score():
    positions = pd.DataFrame([{"ticker": "A", "weight": 0.1, "return_rate": 0.1}])
    decisions = pd.DataFrame([{"ticker": "A", "final_score": 85, "decision": "BUY"}])
    risks = pd.DataFrame([{"ticker": "A", "total_risk_penalty": 0, "leverage_risk": "Normal"}])

    result = generate_portfolio_summary(base_metrics(), positions, decisions, risks, cash_amount=300)

    assert result.overall_score >= 70
    assert result.summary_text


def test_summary_text_is_not_empty_for_normal_case():
    positions = pd.DataFrame([{"ticker": "A", "weight": 0.2, "return_rate": 0.0}])
    decisions = pd.DataFrame([{"ticker": "A", "final_score": 55, "decision": "HOLD"}])
    risks = pd.DataFrame([{"ticker": "A", "total_risk_penalty": -5, "leverage_risk": "Normal"}])

    result = generate_portfolio_summary(base_metrics(), positions, decisions, risks, cash_amount=100)

    assert isinstance(result.summary_text, str)
    assert result.summary_text.strip()
