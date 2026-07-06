from __future__ import annotations

from modules.config.app_tier import can_use_feature, get_app_tier, is_free, is_premium, is_pro


def test_default_app_tier_is_free():
    assert get_app_tier() == "FREE"
    assert is_free() is True
    assert is_pro() is False
    assert is_premium() is False


def test_can_use_feature_for_known_and_unknown_features():
    assert can_use_feature("morning_brief") is True
    assert can_use_feature("advanced_portfolio_engine") is False
    assert can_use_feature("unknown_feature") is False
