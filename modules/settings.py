from __future__ import annotations

APP_SETTINGS: dict[str, object] = {
    "max_portfolio_items": None,
    "enable_paid_plan_limit": False,
    "cash_warning_ratio": 20,
    "single_position_warning_ratio": 30,
}


def get_setting(name: str, default: object = None) -> object:
    """Return one application setting value."""

    return APP_SETTINGS.get(name, default)


def paid_plan_limit_enabled() -> bool:
    """Return whether paid-plan feature limits are enabled."""

    return bool(APP_SETTINGS.get("enable_paid_plan_limit", False))


def get_max_portfolio_items() -> int | None:
    """Return the configured portfolio item limit, or None for unlimited."""

    value = APP_SETTINGS.get("max_portfolio_items")
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None
