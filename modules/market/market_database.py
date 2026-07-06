from __future__ import annotations

import pandas as pd

from modules.market.master_loader import load_master_database, rebuild_master_database, refresh_krx_master_cache


def get_market_database(force_refresh: bool = False) -> pd.DataFrame:
    """Return the canonical market database used by ticker search."""

    if force_refresh:
        rebuild_master_database()
    return load_master_database()


def refresh_market_database() -> tuple[bool, str]:
    """Refresh the full market database with friendly status output."""

    try:
        data = rebuild_master_database()
        total = sum(len(frame) for frame in data.values())
        return True, f"Market database refreshed. {total} rows cached."
    except Exception:
        return False, "Market database refresh failed. Existing cache will be used if available."


def refresh_krx_database() -> tuple[bool, str]:
    """Refresh only the KRX market database."""

    try:
        frame = refresh_krx_master_cache()
        return True, f"KRX database refreshed. {len(frame)} rows cached."
    except Exception:
        return False, "KRX database refresh failed. Existing cache will be used if available."
