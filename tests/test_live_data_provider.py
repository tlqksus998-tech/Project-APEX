from __future__ import annotations

from datetime import datetime

from modules.data_providers.krx_provider import get_krx_live_price
from modules.data_providers.provider_models import FxRateResult, LivePriceResult, MarketIndexResult
from modules.data_providers.us_market_provider import get_market_index, get_us_live_price


def test_live_price_result_creation():
    result = LivePriceResult("AAPL", "Apple", "US", 100, 1, 0.01, 1000, 100000, 1_000_000, "USD", datetime.now(), "test", True, False)
    assert result.ticker == "AAPL"


def test_fx_rate_result_creation():
    result = FxRateResult("USD/KRW", 1380, datetime.now(), "test", True, False)
    assert result.rate == 1380


def test_market_index_result_creation():
    result = MarketIndexResult("^GSPC", "S&P500", 100, 1, 0.01, datetime.now(), "test", True, False)
    assert result.name == "S&P500"


def test_provider_failure_still_returns_result_object():
    assert get_us_live_price("").is_fallback is True
    assert get_krx_live_price("").is_fallback is True
    assert isinstance(get_market_index("").value, float)
