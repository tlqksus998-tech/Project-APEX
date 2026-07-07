from __future__ import annotations

from modules.data_providers.krx_provider import get_krx_live_price
from modules.data_providers.provider_models import LivePriceResult
from modules.data_providers.us_market_provider import get_us_live_price
from modules.market.ticker_utils import infer_market


def get_live_price(ticker: str, name: str = "", market_hint: str | None = None) -> LivePriceResult:
    """Fetch recent price from the appropriate free provider."""

    market = str(market_hint or infer_market(ticker)).upper()
    if market in {"KR", "KRX", "KOSPI", "KOSDAQ", "KONEX"}:
        return get_krx_live_price(ticker, name)
    return get_us_live_price(ticker, name)


def get_live_prices(items: list[tuple[str, str, str | None]]) -> list[LivePriceResult]:
    """Fetch recent prices for ticker/name/market tuples."""

    return [get_live_price(ticker, name, market) for ticker, name, market in items]
