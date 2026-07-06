from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from modules.data_freshness.freshness_models import DataFreshnessSnapshot
from modules.market.master_cache import get_cache_path

KST = ZoneInfo("Asia/Seoul")


def now_kst() -> datetime:
    """Return the current timestamp in Korea time."""

    return datetime.now(KST)


def format_timestamp(value: datetime | None, date_only: bool = False) -> str:
    """Format a timestamp for the Korean dashboard."""

    if value is None:
        return "확인 전"
    localized = value.astimezone(KST) if value.tzinfo else value.replace(tzinfo=KST)
    return localized.strftime("%Y-%m-%d") if date_only else localized.strftime("%Y-%m-%d %H:%M")


def file_mtime(path: Path) -> datetime | None:
    """Return file modified time as KST timestamp when available."""

    try:
        if not path.exists():
            return None
        return datetime.fromtimestamp(path.stat().st_mtime, tz=KST)
    except Exception:
        return None


def mark_analysis_run() -> datetime:
    """Return an analysis execution timestamp."""

    return now_kst()


def build_freshness_snapshot(
    fx_rate: float = 1380.0,
    fx_updated_at: datetime | None = None,
    fx_source: str = "manual",
    price_updated_at: datetime | None = None,
    analysis_run_at: datetime | None = None,
) -> DataFreshnessSnapshot:
    """Build dashboard freshness metadata from known runtime/cache timestamps."""

    current = now_kst()
    krx_updated_at = file_mtime(get_cache_path("krx_master"))
    return DataFreshnessSnapshot(
        data_updated_at=price_updated_at or analysis_run_at or current,
        price_updated_at=price_updated_at,
        fx_updated_at=fx_updated_at,
        krx_master_updated_at=krx_updated_at,
        analysis_run_at=analysis_run_at,
        fx_rate=float(fx_rate or 1380.0),
        fx_source=fx_source or "manual",
    )
