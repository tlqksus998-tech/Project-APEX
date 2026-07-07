from __future__ import annotations

from modules.market.ticker_utils import to_yfinance_ticker


def test_us_tickers_do_not_receive_wrong_suffixes() -> None:
    """US tickers should be passed to yfinance without exchange suffixes."""

    assert to_yfinance_ticker("AAPL", "NASDAQ") == "AAPL"
    assert to_yfinance_ticker("NVDA", "NASDAQ") == "NVDA"
    assert to_yfinance_ticker("TSLA", "NASDAQ") == "TSLA"
    assert to_yfinance_ticker("QQQ", "NASDAQ") == "QQQ"
