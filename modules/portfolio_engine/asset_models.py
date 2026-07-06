from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    """Standard portfolio asset model for the investment operating system."""

    ticker: str
    name: str
    asset_type: str
    market: str
    trading_currency: str
    exposure_region: str
    sector: str = ""
    industry: str = ""
    theme: str = ""
    quantity: float = 0.0
    average_price: float = 0.0
    current_price: float = 0.0
    average_price_original: float = 0.0
    current_price_original: float = 0.0
    value_original_currency: float = 0.0
    fx_rate: float = 1.0
    value_krw: float = 0.0
    weight: float = 0.0
