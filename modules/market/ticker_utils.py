from __future__ import annotations

import re

from modules.market.krx_resolver import is_known_krx_name, krx_name_to_ticker, krx_ticker_to_name, normalize_name


KOSDAQ_HINTS = {"KQ", "KOSDAQ"}
KNOWN_ETF_TICKERS = {
    "SPY",
    "QQQ",
    "DIA",
    "IWM",
    "VOO",
    "VTI",
    "TQQQ",
    "SQQQ",
    "SOXL",
    "SOXS",
    "KORU",
}
US_NAME_ALIASES = {
    "MICRON": "MU",
    "MICRONTECHNOLOGY": "MU",
    "\ub9c8\uc774\ud06c\ub860": "MU",
    "APPLE": "AAPL",
    "APPLEINC": "AAPL",
    "\uc560\ud50c": "AAPL",
}
US_TICKER_NAMES = {
    "MU": "Micron",
    "AAPL": "Apple",
    "KORU": "KORU",
}


def clean_ticker(ticker: str) -> str:
    """Normalize user-entered ticker text while preserving Korean names."""

    return str(ticker or "").strip().upper()


def resolve_us_alias(value: str) -> str | None:
    """Resolve common US company names or Korean aliases to a US ticker."""

    normalized = normalize_name(value)
    return US_NAME_ALIASES.get(normalized)


def is_index_ticker(ticker: str) -> bool:
    """Return True when ticker looks like an index symbol."""

    return clean_ticker(ticker).startswith("^")


def is_korean_stock_ticker(ticker: str) -> bool:
    """Return True for six-digit Korean stock codes or known KRX names."""

    value = clean_ticker(ticker)
    return bool(re.fullmatch(r"\d{6}", value)) or value.endswith((".KS", ".KQ")) or is_known_krx_name(str(ticker))


def is_etf_ticker(ticker: str) -> bool:
    """Return True for known ETF-like ticker strings."""

    return clean_ticker(ticker).replace(".KS", "").replace(".KQ", "") in KNOWN_ETF_TICKERS


def is_us_stock_ticker(ticker: str) -> bool:
    """Return True for common US stock or ETF ticker strings."""

    value = clean_ticker(ticker)
    if resolve_us_alias(str(ticker)):
        return True
    if not value or is_index_ticker(value) or is_korean_stock_ticker(value):
        return False
    return bool(re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", value))


def infer_market(ticker: str, market_hint: str | None = None) -> str:
    """Infer a simple market label from ticker text."""

    hint = clean_ticker(market_hint or "")
    value = clean_ticker(ticker)
    if hint in {"KR", "KS", "KQ", "KOSPI", "KOSDAQ"}:
        return "KR"
    if hint in {"US", "NYSE", "NASDAQ", "AMEX"}:
        return "US"
    if is_index_ticker(value):
        return "INDEX"
    if is_korean_stock_ticker(str(ticker)):
        return "KR"
    if is_us_stock_ticker(str(ticker)):
        return "US"
    return "UNKNOWN"


def resolve_krx_code(ticker_or_name: str) -> str | None:
    """Resolve KRX code from a six-digit ticker, suffixed ticker, or Korean name."""

    value = clean_ticker(ticker_or_name)
    stripped = value.replace(".KS", "").replace(".KQ", "")
    if re.fullmatch(r"\d{6}", stripped):
        return stripped
    return krx_name_to_ticker(str(ticker_or_name))


def resolve_input_symbol(value: str) -> tuple[str, str, str] | None:
    """Resolve one user search value into display name, normalized ticker, and market."""

    raw_value = str(value or "").strip()
    if not raw_value:
        return None

    krx_code = resolve_krx_code(raw_value)
    if krx_code:
        return display_name(krx_code), krx_code, "KR"

    us_alias = resolve_us_alias(raw_value)
    if us_alias:
        return US_TICKER_NAMES.get(us_alias, raw_value), us_alias, "US"

    ticker = clean_ticker(raw_value)
    if is_us_stock_ticker(ticker):
        return US_TICKER_NAMES.get(ticker, ticker), ticker, "US"
    if is_index_ticker(ticker):
        return ticker, ticker, "INDEX"
    return None


def to_yfinance_ticker(ticker: str, market_hint: str | None = None) -> str:
    """Convert an input ticker, US alias, or Korean name into a yfinance-compatible ticker."""

    value = clean_ticker(ticker)
    hint = clean_ticker(market_hint or "")
    if not value:
        return ""
    if value.endswith((".KS", ".KQ")) or is_index_ticker(value):
        return value

    krx_code = resolve_krx_code(str(ticker))
    if krx_code:
        suffix = ".KQ" if hint in KOSDAQ_HINTS else ".KS"
        return f"{krx_code}{suffix}"
    return resolve_us_alias(str(ticker)) or value


def display_ticker(ticker: str) -> str:
    """Return a clean display ticker, preserving Korean names when provided."""

    code = resolve_krx_code(str(ticker))
    if code and not re.fullmatch(r"\d{6}(\.KS|\.KQ)?", clean_ticker(ticker)):
        return code
    return resolve_us_alias(str(ticker)) or clean_ticker(ticker)


def display_name(ticker_or_name: str) -> str:
    """Return known KRX or US display name when possible."""

    code = resolve_krx_code(ticker_or_name)
    if code:
        return krx_ticker_to_name(code) or str(ticker_or_name)
    us_ticker = resolve_us_alias(str(ticker_or_name)) or clean_ticker(str(ticker_or_name))
    if us_ticker in US_TICKER_NAMES:
        return US_TICKER_NAMES[us_ticker]
    return str(ticker_or_name or "").strip()
