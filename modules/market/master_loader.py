from __future__ import annotations

from functools import lru_cache
from io import StringIO

import pandas as pd
import requests

from modules.market.krx_resolver import ETF_BRANDS, FALLBACK_KRX_NAME_TO_TICKER, get_krx_listing
from modules.market.master_cache import cache_exists, read_master_cache, write_master_cache

try:
    from pykrx import stock
except Exception:  # pragma: no cover - optional dependency fallback
    stock = None

COLUMNS = ["ticker", "name", "english_name", "market", "asset_type", "source"]

FALLBACK_KRX_EXTRA = {
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
}

FALLBACK_US = [
    {"ticker": "AAPL", "name": "Apple Inc.", "english_name": "Apple Inc.", "market": "NASDAQ", "asset_type": "Stock"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "english_name": "Microsoft Corp.", "market": "NASDAQ", "asset_type": "Stock"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "english_name": "NVIDIA Corp.", "market": "NASDAQ", "asset_type": "Stock"},
    {"ticker": "MU", "name": "\ub9c8\uc774\ud06c\ub860", "english_name": "Micron Technology Inc.", "market": "NASDAQ", "asset_type": "Stock"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "english_name": "Tesla Inc.", "market": "NASDAQ", "asset_type": "Stock"},
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust", "english_name": "SPDR S&P 500 ETF Trust", "market": "NYSEARCA", "asset_type": "ETF"},
    {"ticker": "QQQ", "name": "Invesco QQQ Trust", "english_name": "Invesco QQQ Trust", "market": "NASDAQ", "asset_type": "ETF"},
    {"ticker": "SOXL", "name": "Direxion Daily Semiconductor Bull 3X Shares", "english_name": "Direxion Daily Semiconductor Bull 3X Shares", "market": "NYSEARCA", "asset_type": "ETF"},
    {"ticker": "TQQQ", "name": "ProShares UltraPro QQQ", "english_name": "ProShares UltraPro QQQ", "market": "NASDAQ", "asset_type": "ETF"},
    {"ticker": "SQQQ", "name": "ProShares UltraPro Short QQQ", "english_name": "ProShares UltraPro Short QQQ", "market": "NASDAQ", "asset_type": "ETF"},
    {"ticker": "KORU", "name": "Direxion Daily South Korea Bull 3X Shares", "english_name": "Direxion Daily South Korea Bull 3X Shares", "market": "NYSEARCA", "asset_type": "ETF"},
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
    frame["ticker"] = frame["ticker"].str.upper()
    frame = frame[frame["ticker"] != ""]
    return frame.drop_duplicates(subset=["ticker", "market"], keep="last").reset_index(drop=True)


def load_krx_master_from_source() -> pd.DataFrame:
    """Load KRX KOSPI/KOSDAQ/KONEX stock master data with fallback rows."""

    rows: list[dict[str, str]] = []
    try:
        listing = get_krx_listing()
        for row in listing.itertuples(index=False):
            rows.append({"ticker": str(row.ticker).zfill(6), "name": str(row.name), "english_name": "", "market": "KRX", "asset_type": "Stock", "source": "pykrx"})
    except Exception:
        rows = []

    fallback = dict(FALLBACK_KRX_NAME_TO_TICKER)
    fallback.update(FALLBACK_KRX_EXTRA)
    for name, ticker in fallback.items():
        rows.append({"ticker": ticker, "name": name, "english_name": "", "market": "KRX", "asset_type": "Stock", "source": "fallback"})
    return normalize_master_frame(pd.DataFrame(rows))


def load_krx_etf_from_source() -> pd.DataFrame:
    """Load KRX ETF master data with fallback rows."""

    rows: list[dict[str, str]] = []
    if stock is not None:
        try:
            for ticker in stock.get_etf_ticker_list():
                name = stock.get_etf_ticker_name(ticker)
                if name:
                    rows.append({"ticker": str(ticker).zfill(6), "name": str(name), "english_name": "", "market": "KRX", "asset_type": "ETF", "source": "pykrx"})
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
        "krx_master": load_krx_master_from_source(),
        "krx_etf": load_krx_etf_from_source(),
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

    frames = [read_master_cache("krx_master"), read_master_cache("krx_etf"), read_master_cache("us_master")]
    if all(frame.empty for frame in frames):
        frames = [load_krx_master_from_source(), load_krx_etf_from_source(), normalize_master_frame(pd.DataFrame(FALLBACK_US))]
    fallback_us = normalize_master_frame(pd.DataFrame(FALLBACK_US))
    combined = normalize_master_frame(pd.concat([*frames, fallback_us], ignore_index=True))
    return combined
