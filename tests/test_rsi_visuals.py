from __future__ import annotations

from app.ui.indicator_visuals import get_rsi_description, get_rsi_label, normalize_rsi


def test_rsi_labels():
    assert get_rsi_label(25) == "과매도권"
    assert get_rsi_label(35) == "반등 관찰"
    assert get_rsi_label(50) == "중립"
    assert get_rsi_label(65) == "강세"
    assert get_rsi_label(75) == "과열 주의"
    assert get_rsi_label(None) == "데이터 부족"


def test_rsi_description_is_beginner_friendly():
    assert "추격매수" in get_rsi_description(75)
    assert "데이터가 부족" in get_rsi_description(None)


def test_rsi_normalization_clamps_range():
    assert normalize_rsi(-10) == 0.0
    assert normalize_rsi(150) == 100.0
    assert normalize_rsi("bad") is None
