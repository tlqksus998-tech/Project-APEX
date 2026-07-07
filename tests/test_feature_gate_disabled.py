from __future__ import annotations

from modules.config.app_tier import can_use_feature


def test_feature_gate_allows_features_when_disabled():
    assert can_use_feature("morning_brief") is True
    assert can_use_feature("investment_approval") is True
    assert can_use_feature("unknown_future_feature") is True
