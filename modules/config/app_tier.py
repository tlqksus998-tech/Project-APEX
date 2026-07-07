from __future__ import annotations

from modules.config.feature_flags import get_feature_value
from modules.settings import paid_plan_limit_enabled

APP_TIER = "STANDARD"


def get_app_tier() -> str:
    """Return the current app tier."""

    return APP_TIER


def is_free() -> bool:
    """Return whether legacy free-mode limits are active."""

    return False


def is_pro() -> bool:
    """Return whether legacy pro-mode limits are active."""

    return False


def is_premium() -> bool:
    """Return whether legacy premium-mode limits are active."""

    return False


def can_use_feature(feature_name: str) -> bool:
    """Return whether a feature is enabled for the current app tier."""

    if not paid_plan_limit_enabled():
        return True
    value = get_feature_value(feature_name, get_app_tier())
    return bool(value is True or value == "unlimited")
