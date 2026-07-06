from __future__ import annotations

from functools import lru_cache
from io import StringIO

import pandas as pd
import requests

from modules.market.external_fallback_loader import load_external_fallback_master, normalize_krx_short_code
from modules.market.krx_resolver import ETF_BRANDS, FALLBACK_KRX_NAME_TO_TICKER, get_krx_listing, normalize_name
from modules.market.master_cache import cache_exists, read_master_cache, write_master_cache

try:
    from pykrx import stock
except Exception:  # pragma: no cover - optional dependency fallback
    stock = None

COLUMNS = ["ticker", "name", "english_name", "market", "asset_type", "source", "aliases", "search_text"]

FALLBACK_KRX_EXTRA = {
    "\uc0bc\uc131\uc804\uae30": "009150",
    "SK\uc2a4\ud018\uc5b4": "402340",
    "\uc0bc\uc131\ubb3c\uc0b0": "028260",
    "\ud604\ub300\ubaa8\ube44\uc2a4": "012330",
    "LG\ud654\ud559": "051910",
    "LG\uc804\uc790": "066570",
    "LG": "003550",
    "KODEX 200": "069500",
    "KODEX \ucf54\uc2a4\ub2e5150\ub808\ubc84\ub9ac\uc9c0": "233740",
    "ACE \ubbf8\uad6dS&P500": "360200",
    "KOSEF 200": "069660",
    "SOL \ubbf8\uad6dS&P500": "433330",
    "HANARO 200": "293180",
    "RISE 200": "148020",
    "PLUS 200": "152100",
    "TIGER \ubbf8\uad6d\ub098\uc2a4\ub2e5100": "133690",
    "\ub300\ud55c\ud56d\uacf5\uc6b0": "003495",
    "\uc0bc\uc131\uc804\uc790\uc6b0": "005935",
    "SK\ub514\uc564\ub514": "210980",
}

FALLBACK_US = [
    {"ticker": "AAPL", "name": "Apple Inc.", "english_name": "Apple Inc.", "market": "NASDAQ", "asset_type": "Stock", "aliases": "Apple \uc560\ud50c"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "english_name": "Microsoft Corp.", "market": "NASDAQ", "asset_type": "Stock", "aliases": "Microsoft \ub9c8\uc774\ud06c\ub85c\uc18c\ud504\ud2b8"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "english_name": "NVIDIA Corp.", "market": "NASDAQ", "asset_type": "Stock", "aliases": "NVIDIA \uc5d4\ube44\ub514\uc544"},
    {"ticker": "MU", "name": "\ub9c8\uc774\ud06c\ub860", "english_name": "Micron Technology Inc.", "market": "NASDAQ", "asset_type": "Stock", "aliases": "Micron \ub9c8\uc774\ud06c\ub860"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "english_name": "Tesla Inc.", "market": "NASDAQ", "asset_type": "Stock", "aliases": "Tesla \ud14c\uc2ac\ub77c"},
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust", "english_name": "SPDR S&P 500 ETF Trust", "market": "NYSEARCA", "asset_type": "ETF", "aliases": "S&P500 S&P 500"},
    {"ticker": "QQQ", "name": "Invesco QQQ Trust", "english_name": "Invesco QQQ Trust", "market": "NASDAQ", "asset_type": "ETF", "aliases": "Nasdaq 100 \ub098\uc2a4\ub2e5100"},
    {"ticker": "SOXL", "name": "Direxion Daily Semiconductor Bull 3X Shares", "english_name": "Direxion Daily Semiconductor Bull 3X Shares", "market": "NYSEARCA", "asset_type": "ETF"},
    {"ticker": "TQQQ", "name": "ProShares UltraPro QQQ", "english_name": "ProShares UltraPro QQQ", "market": "NASDAQ", "asset_type": "ETF"},
    {"ticker": "SQQQ", "name": "ProShares UltraPro Short QQQ", "english_name": "ProShares UltraPro Short QQQ", "market": "NASDAQ", "asset_type": "ETF"},
    {"ticker": "KORU", "name": "Direxion Daily South Korea Bull 3X Shares", "english_name": "Direxion Daily South Korea Bull 3X Shares", "market": "NYSEARCA", "asset_type": "ETF", "aliases": "Korea 3X"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "english_name": "Broadcom Inc.", "market": "NASDAQ", "asset_type": "Stock", "aliases": "Broadcom \ube0c\ub85c\ub4dc\ucef4"},
]


def normalize_master_frame(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize a market master frame into the canonical schema."""

    if data is None or data.empty:
        return pd.DataFrame(columns=COLUMNS)
    frame = data.copy()
    for column in COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    frame = frame[COLUMNS].copy()
    for column in COLUMNS:
        frame[column] = frame[column].fillna("").astype(str).str.strip()
    frame["ticker"] = frame["ticker"].map(normalize_krx_short_code)
    frame["search_text"] = frame.apply(build_search_text, axis=1)
    frame = frame[frame["ticker"] != ""]
    return frame.drop_duplicates(subset=["ticker", "market"], keep="last").reset_index(drop=True)



def build_search_text(row: pd.Series) -> str:
    """Build space-insensitive searchable text for one instrument."""

    values = [row.get("ticker", ""), row.get("name", ""), row.get("english_name", ""), row.get("aliases", "")]
    return " ".join(normalize_name(str(value)) for value in values if str(value or "").strip())



def classify_krx_asset_type(name: str, ticker: str = "") -> str:
    """Classify KRX instruments into stock, ETF, ETN, REIT, preferred, or other."""

    upper_name = str(name or "").upper()
    if any(upper_name.startswith(brand) for brand in ETF_BRANDS):
        return "ETF"
    if "ETN" in upper_name:
        return "ETN"
    if "??" in str(name or "") or "REIT" in upper_name:
        return "REIT"
    if str(name or "").endswith("?") or str(ticker or "").endswith("5"):
        return "Preferred"
    return "Stock"

def load_kospi_master() -> pd.DataFrame:
    """Load KOSPI stock master data from pykrx with safe fallback rows."""

    return load_krx_market_master("KOSPI")


def load_kosdaq_master() -> pd.DataFrame:
    """Load KOSDAQ stock master data from pykrx with safe fallback rows."""

    return load_krx_market_master("KOSDAQ")


def load_krx_market_master(market: str) -> pd.DataFrame:
    """Load one KRX market from pykrx."""

    rows: list[dict[str, str]] = []
    if stock is not None:
        try:
            for ticker in stock.get_market_ticker_list(market=market):
                name = stock.get_market_ticker_name(ticker)
                if name:
                    rows.append({"ticker": normalize_krx_short_code(ticker), "name": str(name), "english_name": "", "market": market, "asset_type": classify_krx_asset_type(name, ticker), "source": "pykrx"})
        except Exception:
            rows = []
    return normalize_master_frame(pd.DataFrame(rows))


def load_krx_master() -> pd.DataFrame:
    """Load KOSPI, KOSDAQ, KONEX, ETF, and fallback KRX rows."""

    frames = [load_kospi_master(), load_kosdaq_master(), load_krx_market_master("KONEX")]
    frames.append(load_krx_master_from_source())
    frames.append(load_krx_etf_from_source())
    frames.append(load_external_fallback_master())
    return normalize_master_frame(pd.concat(frames, ignore_index=True))


def refresh_krx_master_cache() -> pd.DataFrame:
    """Refresh only the KRX master cache file."""

    frame = load_krx_master()
    write_master_cache("krx_master", frame)
    load_master_database.cache_clear()
    return frame

def load_krx_master_from_source() -> pd.DataFrame:
    """Load KRX KOSPI/KOSDAQ/KONEX stock master data with fallback rows."""

    rows: list[dict[str, str]] = []
    try:
        listing = get_krx_listing()
        for row in listing.itertuples(index=False):
            ticker = normalize_krx_short_code(row.ticker)
            name = str(row.name)
            rows.append({"ticker": ticker, "name": name, "english_name": "", "market": "KRX", "asset_type": classify_krx_asset_type(name, ticker), "source": "pykrx"})
    except Exception:
        rows = []

    fallback = dict(FALLBACK_KRX_NAME_TO_TICKER)
    fallback.update(FALLBACK_KRX_EXTRA)
    for name, ticker in fallback.items():
        rows.append({"ticker": ticker, "name": name, "english_name": "", "market": "KRX", "asset_type": classify_krx_asset_type(name, ticker), "source": "fallback"})
    return normalize_master_frame(pd.DataFrame(rows))


def load_krx_etf_from_source() -> pd.DataFrame:
    """Load KRX ETF master data with fallback rows."""

    rows: list[dict[str, str]] = []
    if stock is not None:
        try:
            for ticker in stock.get_etf_ticker_list():
                name = stock.get_etf_ticker_name(ticker)
                if name:
                    rows.append({"ticker": normalize_krx_short_code(ticker), "name": str(name), "english_name": "", "market": "KRX", "asset_type": "ETF", "source": "pykrx"})
        except Exception:
            rows = []

    fallback = dict(FALLBACK_KRX_NAME_TO_TICKER)
    fallback.update(FALLBACK_KRX_EXTRA)
    for name, ticker in fallback.items():
        if any(str(name).upper().startswith(brand) for brand in ETF_BRANDS):
            rows.append({"ticker": ticker, "name": name, "english_name": "", "market": "KRX", "asset_type": "ETF", "source": "fallback"})
    return normalize_master_frame(pd.DataFrame(rows))


def load_us_master_from_source(timeout: int = 8) -> pd.DataFrame:
    """Load US listed symbols from Nasdaq Trader with representative ETF fallback rows."""

    rows: list[dict[str, str]] = []
    sources = [
        ("NASDAQ", "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"),
        ("OTHER", "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"),
    ]
    for market_label, url in sources:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            text = "\n".join(line for line in response.text.splitlines() if not line.startswith("File Creation Time"))
            data = pd.read_csv(StringIO(text), sep="|")
            for row in data.itertuples(index=False):
                ticker = str(getattr(row, "Symbol", getattr(row, "ACT_Symbol", ""))).strip()
                name = str(getattr(row, "Security_Name", "")).strip()
                if not ticker or ticker == "nan" or ticker == "Symbol":
                    continue
                asset_type = "ETF" if "ETF" in name.upper() or "FUND" in name.upper() or ticker in {"SPY", "QQQ", "SOXL", "TQQQ", "SQQQ", "KORU"} else "Stock"
                rows.append({"ticker": ticker, "name": name, "english_name": name, "market": market_label, "asset_type": asset_type, "source": "nasdaqtrader"})
        except Exception:
            continue

    for row in FALLBACK_US:
        rows.append({**row, "source": "fallback"})
    return normalize_master_frame(pd.DataFrame(rows))


def rebuild_master_database() -> dict[str, pd.DataFrame]:
    """Refresh all master datasets and write them to cache."""

    data = {
        "krx_master": load_krx_master(),
        "krx_etf": load_krx_etf_from_source(),
        "krx_external": load_external_fallback_master(),
        "us_master": load_us_master_from_source(),
    }
    for name, frame in data.items():
        write_master_cache(name, frame)
    load_master_database.cache_clear()
    return data


@lru_cache(maxsize=1)
def load_master_database() -> pd.DataFrame:
    """Load combined master database from cache, creating it on first use."""

    if not cache_exists():
        try:
            rebuild_master_database()
        except Exception:
            pass

    frames = [read_master_cache("krx_master"), read_master_cache("krx_etf"), read_master_cache("krx_external"), read_master_cache("us_master")]
    if all(frame.empty for frame in frames):
        frames = [load_krx_master_from_source(), load_krx_etf_from_source(), normalize_master_frame(pd.DataFrame(FALLBACK_US))]
    fallback_krx = load_krx_master_from_source()
    fallback_external = load_external_fallback_master()
    fallback_us = normalize_master_frame(pd.DataFrame(FALLBACK_US))
    # Put fallback rows last so alias/search_text upgrades override old cache rows.
    combined = normalize_master_frame(pd.concat([*frames, fallback_krx, fallback_external, fallback_us], ignore_index=True))
    return combined

