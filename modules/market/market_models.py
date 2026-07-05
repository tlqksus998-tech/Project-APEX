from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class MarketDataRequest:
    """Request options for market data providers."""

    ticker: str
    period: str = "6mo"
    interval: str = "1d"
    market_hint: str | None = None


@dataclass(frozen=True)
class PriceData:
    """Current price response returned by the Market Engine."""

    ticker: str
    display_ticker: str
    market: str
    current_price: float
    currency: str
    source: str
    success: bool
    message: str


@dataclass(frozen=True)
class OHLCVDataResult:
    """OHLCV response returned by the Market Engine."""

    ticker: str
    display_ticker: str
    market: str
    data: pd.DataFrame
    source: str
    success: bool
    message: str
