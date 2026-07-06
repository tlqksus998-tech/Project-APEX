from __future__ import annotations

from modules.config.feature_flags import get_feature_flags, get_feature_value, is_unlimited


def test_free_portfolio_limit_is_five():
    assert get_feature_value("max_portfolio_positions", "FREE") == 5
    assert get_feature_value("watchlist_limit", "FREE") == 3


def test_pro_has_unlimited_limits():
    assert is_unlimited(get_feature_value("max_portfolio_positions", "PRO"))
    assert is_unlimited(get_feature_value("watchlist_limit", "PRO"))
    assert get_feature_value("investment_approval", "PRO") is True


def test_unknown_feature_returns_false():
    assert get_feature_value("does_not_exist", "FREE") is False
    assert get_feature_flags("UNKNOWN")["max_portfolio_positions"] == 5
