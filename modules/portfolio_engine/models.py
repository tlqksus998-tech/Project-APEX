from __future__ import annotations

from dataclasses import dataclass, field

from modules.portfolio_engine.asset_models import Asset


@dataclass(frozen=True)
class PortfolioEngineSnapshot:
    """Portfolio operating snapshot for dashboard header metrics."""

    assets: list[Asset] = field(default_factory=list)
    total_assets_krw: float = 0.0
    total_invested_krw: float = 0.0
    total_cash_krw: float = 0.0
    cash_ratio: float = 0.0
    krw_cash: float = 0.0
    usd_cash: float = 0.0
    usdkrw: float = 1380.0
    krw_weight: float = 0.0
    usd_weight: float = 0.0
    korea_exposure: float = 0.0
    us_exposure: float = 0.0
    investable_cash_krw: float = 0.0
    market_weights: dict[str, float] = field(default_factory=dict)
    currency_weights: dict[str, float] = field(default_factory=dict)
