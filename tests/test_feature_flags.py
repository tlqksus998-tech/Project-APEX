from __future__ import annotations

from modules.config.feature_flags import get_feature_flags, get_feature_value, is_unlimited


def test_default_portfolio_limits_are_unlimited():
    assert is_unlimited(get_feature_value("max_portfolio_positions"))
    assert is_unlimited(get_feature_value("watchlist_limit"))


def test_all_core_flags_enabled():
    assert get_feature_value("investment_approval") is True
    assert get_feature_value("advanced_portfolio_engine") is True
    assert get_feature_value("currency_exposure_analysis") is True


def test_unknown_feature_returns_false():
    assert get_feature_value("does_not_exist") is False
    assert is_unlimited(get_feature_flags("UNKNOWN")["max_portfolio_positions"])
