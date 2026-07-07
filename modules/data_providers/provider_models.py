from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LivePriceResult:
    """Common live/recent price result."""

    ticker: str
    name: str
    market: str
    price: float
    change: float
    change_pct: float
    volume: float
    trading_value: float
    market_cap: float
    currency: str
    updated_at: datetime
    source: str
    success: bool
    is_fallback: bool
    error_message: str = ""


@dataclass(frozen=True)
class FxRateResult:
    """Common FX rate result."""

    pair: str
    rate: float
    updated_at: datetime
    source: str
    success: bool
    is_fallback: bool
    error_message: str = ""


@dataclass(frozen=True)
class MarketIndexResult:
    """Common market index result."""

    symbol: str
    name: str
    value: float
    change: float
    change_pct: float
    updated_at: datetime
    source: str
    success: bool
    is_fallback: bool
    error_message: str = ""
