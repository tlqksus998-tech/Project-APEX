from modules.market.ticker_utils import (
    infer_market,
    is_index_ticker,
    is_korean_stock_ticker,
    is_us_stock_ticker,
    resolve_input_symbol,
    resolve_us_alias,
    to_yfinance_ticker,
)

SAMSUNG = "\uc0bc\uc131\uc804\uc790"
SK_HYNIX = "SK\ud558\uc774\ub2c9\uc2a4"
MIRAE = "\ubbf8\ub798\uc5d0\uc14b\ubca4\ucc98\ud22c\uc790"
NEXON = "\ub125\uc2a8\uac8c\uc784\uc988"
TIGER_SP500 = "TIGER \ubbf8\uad6dS&P500"
MICRON_KO = "\ub9c8\uc774\ud06c\ub860"


def test_korean_stock_ticker_detection():
    assert is_korean_stock_ticker("005930")
    assert is_korean_stock_ticker("000660")
    assert is_korean_stock_ticker(SAMSUNG)
    assert to_yfinance_ticker("005930") == "005930.KS"
    assert to_yfinance_ticker("005930", "KQ") == "005930.KQ"
    assert to_yfinance_ticker(SK_HYNIX) == "000660.KS"


def test_us_and_index_ticker_detection():
    assert is_us_stock_ticker("AAPL")
    assert is_us_stock_ticker("TSLA")
    assert is_us_stock_ticker("SPY")
    assert is_us_stock_ticker(MICRON_KO)
    assert is_index_ticker("^VIX")
    assert infer_market("^VIX") == "INDEX"


def test_requested_korean_inputs_resolve_to_real_tickers():
    assert resolve_input_symbol(SAMSUNG) == (SAMSUNG, "005930", "KR")
    assert resolve_input_symbol(SK_HYNIX) == (SK_HYNIX, "000660", "KR")
    assert resolve_input_symbol(MIRAE) == (MIRAE, "100790", "KR")
    assert resolve_input_symbol(NEXON) == (NEXON, "225570", "KR")
    assert resolve_input_symbol(TIGER_SP500) == (TIGER_SP500, "360750", "KR")


def test_us_name_aliases_resolve_to_tickers():
    assert resolve_us_alias(MICRON_KO) == "MU"
    assert resolve_us_alias("Micron") == "MU"
    assert resolve_us_alias("Apple") == "AAPL"
    assert resolve_input_symbol(MICRON_KO) == ("Micron", "MU", "US")
    assert resolve_input_symbol("KORU") == ("KORU", "KORU", "US")
    assert resolve_input_symbol("MU") == ("Micron", "MU", "US")
    assert to_yfinance_ticker(MICRON_KO) == "MU"
