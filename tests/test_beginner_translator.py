from __future__ import annotations

from modules.beginner.explain_translator import (
    build_beginner_reasons,
    build_beginner_warnings,
    decision_to_easy_label,
    describe_interest,
    describe_price_position,
    describe_risk,
    describe_trend,
)


def test_decision_to_easy_label_hides_english_decisions():
    for signal in ["STRONG_BUY", "BUY", "HOLD", "REDUCE", "SELL"]:
        label = decision_to_easy_label(signal)
        assert label
        assert signal not in label


def test_beginner_indicator_translation_returns_plain_sentences():
    outputs = [
        describe_price_position(85),
        describe_trend("상승추세", ""),
        describe_interest("거래량 증가"),
        describe_risk("SELL"),
    ]
    assert all(isinstance(value, str) and value for value in outputs)
    assert all("MACD" not in value and "RSI" not in value for value in outputs)


def test_beginner_reasons_and_warnings_are_plain_korean():
    analysis = {"volume_status": "거래량 증가", "trend_status": "상승추세", "macd_status": "상승 모멘텀", "rsi_14": 50}
    decision = {"final_score": 80, "final_decision": "BUY"}

    reasons = build_beginner_reasons(analysis, decision)
    warnings = build_beginner_warnings(analysis, decision)

    assert len(reasons) == 3
    assert len(warnings) == 2
    assert all("BUY" not in item and "RSI" not in item for item in reasons + warnings)
