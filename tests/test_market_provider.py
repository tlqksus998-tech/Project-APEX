from modules.config import get_config
from modules.market.market_models import MarketDataRequest, OHLCVDataResult, PriceData
from modules.market.ohlcv_provider import get_ohlcv
from modules.market.price_provider import get_current_price


def test_get_current_price_returns_price_data_for_bad_ticker():
    config = get_config()
    price = get_current_price("BAD_TEST_TICKER_DO_NOT_EXIST", config)

    assert isinstance(price, PriceData)
    assert price.current_price > 0
    assert price.success is False
    assert price.source == "fallback"


def test_get_ohlcv_returns_standard_columns_for_bad_ticker():
    config = get_config()
    result = get_ohlcv(MarketDataRequest("BAD_TEST_TICKER_DO_NOT_EXIST"), config)

    assert isinstance(result, OHLCVDataResult)
    assert list(result.data.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert not result.data.empty
    assert result.success is False
