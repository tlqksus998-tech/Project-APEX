import pandas as pd

from modules.config import get_config
from modules.market.krx_resolver import krx_name_to_ticker, krx_ticker_to_name, suggest_krx_names
from modules.market.market_models import MarketDataRequest
from modules.market.ohlcv_provider import get_ohlcv
from modules.market.ticker_utils import infer_market, is_korean_stock_ticker, is_us_stock_ticker, to_yfinance_ticker
from modules.portfolio.input_data import validate_portfolio

SAMSUNG = "\uc0bc\uc131\uc804\uc790"
SAMSUNG_SDI = "\uc0bc\uc131SDI"
SK_HYNIX = "SK\ud558\uc774\ub2c9\uc2a4"
MICRON_KO = "\ub9c8\uc774\ud06c\ub860"
MIRAE = "\ubbf8\ub798\uc5d0\uc14b\ubca4\ucc98\ud22c\uc790"
NEXON = "\ub125\uc2a8\uac8c\uc784\uc988"
TIGER_SP500 = "TIGER \ubbf8\uad6dS&P500"


def test_krx_name_to_ticker_fallback_core_names():
    assert krx_name_to_ticker(SK_HYNIX) == "000660"
    assert krx_name_to_ticker(MIRAE) == "100790"
    assert krx_name_to_ticker(NEXON) == "225570"
    assert krx_name_to_ticker(TIGER_SP500) == "360750"
    assert krx_ticker_to_name("005930") == SAMSUNG


def test_korean_and_us_market_detection():
    assert is_korean_stock_ticker(SAMSUNG)
    assert is_korean_stock_ticker("005930")
    assert infer_market(SK_HYNIX) == "KR"
    assert to_yfinance_ticker(SK_HYNIX) == "000660.KS"
    assert is_us_stock_ticker("KORU")
    assert is_us_stock_ticker("MU")


def test_samsung_autocomplete_suggestions():
    suggestions = suggest_krx_names("\uc0bc\uc131")
    assert SAMSUNG in suggestions
    assert SAMSUNG_SDI in suggestions


def test_portfolio_accepts_requested_real_inputs():
    raw = pd.DataFrame(
        [
            {"name": SK_HYNIX, "ticker": SK_HYNIX, "quantity": 1, "avg_price": 180000},
            {"name": "KORU", "ticker": "KORU", "quantity": 1, "avg_price": 10},
            {"name": MICRON_KO, "ticker": "MU", "quantity": 1, "avg_price": 100},
            {"name": MIRAE, "ticker": MIRAE, "quantity": 1, "avg_price": 6000},
            {"name": NEXON, "ticker": NEXON, "quantity": 1, "avg_price": 15000},
            {"name": TIGER_SP500, "ticker": TIGER_SP500, "quantity": 1, "avg_price": 20000},
        ]
    )
    portfolio, errors = validate_portfolio(raw)

    assert errors == []
    assert portfolio["ticker"].tolist() == ["000660", "KORU", "MU", "100790", "225570", "360750"]


def test_ohlcv_supports_korean_name_with_safe_result():
    result = get_ohlcv(MarketDataRequest(SK_HYNIX), get_config())

    assert result.market == "KR"
    assert result.display_ticker == "000660"
    assert not result.data.empty
    assert list(result.data.columns) == ["date", "open", "high", "low", "close", "volume"]
