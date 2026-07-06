from __future__ import annotations

UNLIMITED = "unlimited"

FEATURE_FLAGS = {
    "FREE": {
        "morning_brief": True,
        "macro_dashboard": True,
        "basic_portfolio": True,
        "max_portfolio_positions": 5,
        "basic_risk_alert": True,
        "watchlist_limit": 3,
        "advanced_portfolio_engine": False,
        "full_watchlist": False,
        "currency_exposure_analysis": False,
        "sector_exposure_analysis": False,
        "investment_approval": False,
        "pro_candidate_reason": False,
    },
    "PRO": {
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
    "PREMIUM": {
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
        "ai_report": False,
        "investment_history": False,
        "performance_analysis": False,
    },
}


def get_feature_flags(tier: str = "FREE") -> dict[str, object]:
    """Return feature flags for a tier with FREE fallback."""

    normalized = str(tier or "FREE").upper()
    return FEATURE_FLAGS.get(normalized, FEATURE_FLAGS["FREE"]).copy()


def get_feature_value(feature_name: str, tier: str = "FREE") -> object:
    """Return one feature value or False when unknown."""

    return get_feature_flags(tier).get(feature_name, False)


def is_unlimited(value: object) -> bool:
    """Return True for unlimited feature values."""

    return value == UNLIMITED
