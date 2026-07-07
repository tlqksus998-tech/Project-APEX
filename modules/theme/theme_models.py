from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ThemeAsset:
    """One asset mapped to an investment theme."""

    name: str
    ticker: str
    market: str


@dataclass(frozen=True)
class ThemeStrengthResult:
    """Theme strength summary from related asset moves."""

    theme: str
    avg_change_pct: float
    positive_count: int
    negative_count: int
    total_count: int
    strength_label: str
    representative_tickers: list[str]
    updated_at: datetime
    source: str
    success: bool
    is_fallback: bool
    error_message: str = ""
