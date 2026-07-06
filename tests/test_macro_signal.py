from __future__ import annotations

from datetime import datetime

from modules.market.macro_models import MacroIndicator
from modules.market.macro_signal import VALID_MARKET_SIGNALS, calculate_apex_macro_score, classify_market_signal


def make_indicator(name: str, change_pct: float, status: str = "OK") -> MacroIndicator:
    return MacroIndicator(
        symbol=name,
        name=name,
        value=100.0,
        change=100.0 * change_pct,
        change_pct=change_pct,
        currency="USD",
        status=status,
        updated_at=datetime.now(),
        source="test",
    )


def test_macro_score_range_and_signal_values():
    indicators = [
        make_indicator("S&P500", 0.01),
        make_indicator("NASDAQ", 0.012),
        make_indicator("KOSPI", 0.004),
        make_indicator("KOSDAQ", 0.002),
        make_indicator("VIX", -0.02),
        make_indicator("USD/KRW", -0.003),
        make_indicator("Gold", 0.001),
        make_indicator("WTI", 0.001),
    ]

    score = calculate_apex_macro_score(indicators)
    signal, label, message = classify_market_signal(score)

    assert 0 <= score <= 100
    assert signal in VALID_MARKET_SIGNALS
    assert label
    assert message


def test_macro_score_penalizes_risk_conditions():
    favorable = calculate_apex_macro_score([make_indicator("S&P500", 0.01), make_indicator("VIX", -0.02)])
    risky = calculate_apex_macro_score([make_indicator("S&P500", -0.02), make_indicator("VIX", 0.05), make_indicator("USD/KRW", 0.03)])

    assert risky < favorable
