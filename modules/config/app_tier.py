from __future__ import annotations

from modules.config.feature_flags import get_feature_value

APP_TIER = "FREE"
SUPPORTED_TIERS = {"FREE", "PRO", "PREMIUM"}


def get_app_tier() -> str:
    """Return the current app tier."""

    tier = str(APP_TIER or "FREE").upper()
    return tier if tier in SUPPORTED_TIERS else "FREE"


def is_free() -> bool:
    """Return True when the app runs in Free mode."""

    return get_app_tier() == "FREE"


def is_pro() -> bool:
    """Return True when the app runs in Pro mode."""

    return get_app_tier() == "PRO"


def is_premium() -> bool:
    """Return True when the app runs in Premium mode."""

    return get_app_tier() == "PREMIUM"


def can_use_feature(feature_name: str) -> bool:
    """Return whether a feature is enabled for the current app tier."""

    value = get_feature_value(feature_name, get_app_tier())
    return bool(value is True or value == "unlimited")
