from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MARKET_DATA_DIR = PROJECT_ROOT / "data" / "market"
CACHE_FILES = {
    "krx_master": MARKET_DATA_DIR / "krx_master.parquet",
    "krx_etf": MARKET_DATA_DIR / "krx_etf.parquet",
    "us_master": MARKET_DATA_DIR / "us_master.parquet",
}


def ensure_market_data_dir() -> Path:
    """Ensure the market master cache directory exists."""

    MARKET_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return MARKET_DATA_DIR


def get_cache_path(name: str) -> Path:
    """Return the cache path for a named master dataset."""

    ensure_market_data_dir()
    return CACHE_FILES[name]


def write_master_cache(name: str, data: pd.DataFrame) -> Path:
    """Write a master dataset using parquet when possible and pickle fallback otherwise."""

    path = get_cache_path(name)
    frame = data.copy()
    try:
        frame.to_parquet(path, index=False)
    except Exception:
        frame.to_pickle(path)
    return path


def read_master_cache(name: str) -> pd.DataFrame:
    """Read a cached master dataset from parquet or pickle fallback."""

    path = get_cache_path(name)
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        try:
            return pd.read_pickle(path)
        except Exception:
            return pd.DataFrame()


def cache_exists() -> bool:
    """Return True when all master cache files exist."""

    return all(path.exists() for path in CACHE_FILES.values())


def clear_master_memory_cache() -> None:
    """Clear lru/cache_data-like in-process caches owned by master modules."""

    try:
        from modules.market.master_loader import load_master_database
        from modules.market.master_search import search_instruments

        load_master_database.cache_clear()
        search_instruments.cache_clear()
    except Exception:
        return
