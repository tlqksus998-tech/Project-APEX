from __future__ import annotations

from modules.theme.theme_strength import calculate_theme_strength, classify_strength


def test_theme_strength_label_returns_expected_values():
    assert classify_strength(0.02) == "강한 강세"
    assert classify_strength(0.005) == "강세"
    assert classify_strength(0.0) == "중립"
    assert classify_strength(-0.005) == "약세"
    assert classify_strength(-0.02) == "강한 약세"


def test_theme_strength_result_calculates():
    result = calculate_theme_strength("없는테마")
    assert result.theme == "없는테마"
    assert result.total_count == 0
    assert result.is_fallback is True
