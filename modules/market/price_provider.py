from __future__ import annotations

import logging

import pandas as pd

from modules.config import AppConfig
from modules.market.market_models import MarketDataRequest, PriceData
from modules.market.ohlcv_provider import get_ohlcv
from modules.market.ticker_utils import display_ticker, infer_market, to_yfinance_ticker


logger = logging.getLogger(__name__)


def get_current_price(ticker: str, config: AppConfig, market_hint: str | None = None) -> PriceData:
    """Fetch current price data with a safe fallback response."""

    display = display_ticker(ticker)
    yf_ticker = to_yfinance_ticker(ticker, market_hint)
    market = infer_market(ticker, market_hint)
    if not yf_ticker:
        return PriceData("", display, market, config.dummy_price, "USD", "fallback", False, "Invalid ticker")

    request = MarketDataRequest(ticker=ticker, period="5d", interval="1d", market_hint=market_hint)
    result = get_ohlcv(request, config)
    if result.data.empty:
        logger.info("Current price unavailable for %s", yf_ticker)
        return PriceData(yf_ticker, display, market, config.dummy_price, currency_for_market(market), "fallback", False, "Current price unavailable")

    current_price = float(result.data.sort_values("date").iloc[-1]["close"])
    success = bool(result.success and current_price > 0)
    source = result.source if success else "fallback"
    message = "OK" if success else "Fallback price returned"
    return PriceData(yf_ticker, display, market, current_price, currency_for_market(market), source, success, message)


def get_current_prices(tickers: list[str], config: AppConfig) -> pd.DataFrame:
    """Fetch current prices for portfolio tickers as a DataFrame."""

    rows: list[dict[str, object]] = []
    for ticker in tickers:
        price = get_current_price(ticker, config)
        rows.append(
            {
                "ticker": price.display_ticker,
                "provider_ticker": price.ticker,
                "market": price.market,
                "current_price": price.current_price,
                "currency": price.currency,
                "price_source": price.source,
                "success": price.success,
                "message": price.message,
            }
        )
    return pd.DataFrame(rows)


def currency_for_market(market: str) -> str:
    """Return a simple default currency for a market label."""

    return "KRW" if market == "KR" else "USD"
