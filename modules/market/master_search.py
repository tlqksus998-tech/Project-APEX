from __future__ import annotations

from functools import lru_cache
from time import perf_counter

import pandas as pd

from modules.market.krx_resolver import normalize_name
from modules.market.master_cache import clear_master_memory_cache
from modules.market.master_loader import load_master_database, rebuild_master_database, refresh_krx_master_cache

RESULT_COLUMNS = ["ticker", "name", "english_name", "market", "asset_type", "score", "label"]


def normalize_search_text(value: str) -> str:
    """Normalize query text for case-insensitive and space-insensitive search."""

    return normalize_name(value)


def prepare_search_frame() -> pd.DataFrame:
    """Return the master database with normalized searchable columns."""

    frame = load_master_database().copy()
    if frame.empty:
        return frame
    frame["_ticker_norm"] = frame["ticker"].map(normalize_search_text)
    frame["_name_norm"] = frame["name"].map(normalize_search_text)
    frame["_english_norm"] = frame["english_name"].map(normalize_search_text)
    if "search_text" in frame.columns:
        frame["_cached_search_norm"] = frame["search_text"].map(normalize_search_text)
    else:
        frame["_cached_search_norm"] = ""
    frame["_search_blob"] = frame["_ticker_norm"] + " " + frame["_name_norm"] + " " + frame["_english_norm"] + " " + frame["_cached_search_norm"]
    return frame


def score_row(row: pd.Series, query: str) -> int:
    """Score one instrument search result."""

    ticker = str(row.get("_ticker_norm", ""))
    name = str(row.get("_name_norm", ""))
    english = str(row.get("_english_norm", ""))
    blob = str(row.get("_search_blob", ""))
    score = 0
    if query == ticker:
        score += 120
    if query == name or query == english:
        score += 110
    if ticker.startswith(query):
        score += 80
    if name.startswith(query) or english.startswith(query):
        score += 70
    if query in ticker:
        score += 45
    if query in name:
        score += 40
    if query in english:
        score += 35
    if query in blob:
        score += 10
    if row.get("asset_type") == "ETF":
        score += 3
    return score


@lru_cache(maxsize=512)
def search_instruments(query: str, limit: int = 30) -> tuple[tuple[str, str, str, str, str, int, str], ...]:
    """Search Korean/US stocks and ETFs and return ranked immutable rows."""

    normalized_query = normalize_search_text(query)
    if not normalized_query:
        return tuple()

    frame = prepare_search_frame()
    if frame.empty:
        return tuple()

    mask = frame["_search_blob"].str.contains(normalized_query, regex=False, na=False)
    matches = frame.loc[mask].copy()
    if matches.empty:
        return tuple()
    matches["score"] = matches.apply(lambda row: score_row(row, normalized_query), axis=1)
    matches = matches[matches["score"] > 0]
    matches["label"] = matches.apply(format_search_label, axis=1)
    matches = matches.sort_values(["score", "ticker"], ascending=[False, True]).head(limit)
    return tuple(tuple(row) for row in matches[RESULT_COLUMNS].itertuples(index=False, name=None))


def format_search_label(row: pd.Series) -> str:
    """Format a search result label for the UI."""

    name = str(row.get("name", "")).strip() or str(row.get("english_name", "")).strip()
    ticker = str(row.get("ticker", "")).strip()
    market = str(row.get("market", "")).strip()
    asset_type = str(row.get("asset_type", "")).strip()
    return f"{name} ({ticker}) ? {market} ? {asset_type}"


def search_as_dataframe(query: str, limit: int = 30) -> pd.DataFrame:
    """Search instruments and return a DataFrame for tests or UI."""

    rows = search_instruments(query, limit)
    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


def search_master(query: str, limit: int = 30) -> pd.DataFrame:
    """Search the master database with the Sprint 3.7 public API name."""

    return search_as_dataframe(query, limit)


def refresh_krx_master_database() -> tuple[bool, str]:
    """Refresh KRX stock master cache only."""

    try:
        frame = refresh_krx_master_cache()
        clear_master_memory_cache()
        return True, f"KRX stock database updated. {len(frame)} rows cached."
    except Exception:
        return False, "KRX database update failed. Existing cache will be used if available."


def refresh_master_database() -> tuple[bool, str]:
    """Refresh master database cache and clear in-memory search caches."""

    try:
        data = rebuild_master_database()
        clear_master_memory_cache()
        total = sum(len(frame) for frame in data.values())
        return True, f"Market master database updated. {total} rows cached."
    except Exception:
        return False, "Market data update failed. Existing cache will be used if available."


def measure_search_latency(query: str) -> float:
    """Return elapsed search latency in seconds for a query."""

    started = perf_counter()
    search_instruments(query, 30)
    return perf_counter() - started
