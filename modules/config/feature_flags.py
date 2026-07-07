from __future__ import annotations

UNLIMITED = "unlimited"

FEATURE_FLAGS = {
    "STANDARD": {
        "morning_brief": True,
        "macro_dashboard": True,
        "basic_portfolio": True,
        "max_portfolio_positions": UNLIMITED,
        "basic_risk_alert": True,
        "watchlist_limit": UNLIMITED,
        "advanced_portfolio_engine": True,
        "full_watchlist": True,
        "currency_exposure_analysis": True,
        "sector_exposure_analysis": True,
        "investment_approval": True,
        "pro_candidate_reason": True,
    },
}


def get_feature_flags(tier: str = "STANDARD") -> dict[str, object]:
    """Return unrestricted feature flags."""

    return FEATURE_FLAGS["STANDARD"].copy()


def get_feature_value(feature_name: str, tier: str = "STANDARD") -> object:
    """Return one feature value or False when unknown."""

    return get_feature_flags(tier).get(feature_name, False)


def is_unlimited(value: object) -> bool:
    """Return True for unlimited feature values."""

    return value == UNLIMITED
