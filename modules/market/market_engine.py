from __future__ import annotations

import pandas as pd

from modules.config import AppConfig
from modules.market.market_models import MarketDataRequest
from modules.market.ohlcv_provider import get_ohlcv
from modules.market.price_provider import get_current_price


def build_market_overview(
    tickers: list[str],
    config: AppConfig,
    period: str | None = None,
    interval: str | None = None,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Build overview rows and OHLCV histories for dashboard display."""

    rows: list[dict[str, object]] = []
    histories: dict[str, pd.DataFrame] = {}
    unique_tickers = list(dict.fromkeys(str(ticker).upper().strip() for ticker in tickers if str(ticker).strip()))

    for ticker in unique_tickers:
        request = MarketDataRequest(ticker=ticker, period=period or "6mo", interval=interval or "1d")
        ohlcv = get_ohlcv(request, config)
        price = get_current_price(ticker, config)
        history = ohlcv.data.copy()
        histories[price.display_ticker] = history

        previous_close = latest_previous_close(history)
        current_price = price.current_price
        first_close = float(history.iloc[0]["close"]) if not history.empty else 0.0
        daily_return = (current_price / previous_close - 1) if previous_close > 0 else 0.0
        period_return = (current_price / first_close - 1) if first_close > 0 else 0.0

        rows.append(
            {
                "ticker": price.display_ticker,
                "provider_ticker": price.ticker,
                "market": price.market,
                "current_price": current_price,
                "currency": price.currency,
                "source": price.source,
                "success": price.success,
                "message": price.message,
                "previous_close": previous_close,
                "daily_return": daily_return,
                "period_return": period_return,
            }
        )

    return pd.DataFrame(rows), histories


def latest_previous_close(history: pd.DataFrame) -> float:
    """Return the previous close when available."""

    if history.empty:
        return 0.0
    ordered = history.sort_values("date").reset_index(drop=True)
    row = ordered.iloc[-2] if len(ordered) > 1 else ordered.iloc[-1]
    return float(row["close"])
