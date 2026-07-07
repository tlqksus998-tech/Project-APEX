from __future__ import annotations

from modules.settings import get_max_portfolio_items, get_setting, paid_plan_limit_enabled


def test_default_settings_disable_paid_limits():
    assert paid_plan_limit_enabled() is False
    assert get_max_portfolio_items() is None
    assert get_setting("cash_warning_ratio") == 20
