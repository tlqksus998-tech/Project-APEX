from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DataFreshnessSnapshot:
    """Display-ready timestamps for market data freshness."""

    data_updated_at: datetime
    price_updated_at: datetime | None = None
    fx_updated_at: datetime | None = None
    krx_master_updated_at: datetime | None = None
    analysis_run_at: datetime | None = None
    fx_rate: float = 1380.0
    fx_source: str = "manual"
