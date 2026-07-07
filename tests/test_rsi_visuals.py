from __future__ import annotations

from app.ui.indicator_visuals import get_rsi_description, get_rsi_label, normalize_rsi


def test_rsi_labels():
    assert get_rsi_label(25) == "많이 내려왔어요"
    assert get_rsi_label(35) == "반등을 볼 자리예요"
    assert get_rsi_label(50) == "차분한 편이에요"
    assert get_rsi_label(65) == "힘이 있어요"
    assert get_rsi_label(75) == "조금 뜨거워요"
    assert get_rsi_label(None) == "데이터 부족"


def test_rsi_description_is_beginner_friendly():
    assert "조심" in get_rsi_description(75)
    assert "데이터가 부족" in get_rsi_description(None)


def test_rsi_normalization_clamps_range():
    assert normalize_rsi(-10) == 0.0
    assert normalize_rsi(150) == 100.0
    assert normalize_rsi("bad") is None
