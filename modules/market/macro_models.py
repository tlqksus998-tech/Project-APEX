from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class MacroIndicator:
    """One macro indicator with price, change, and chart data."""

    symbol: str
    name: str
    value: float
    change: float
    change_pct: float
    currency: str
    status: str
    updated_at: datetime
    source: str
    chart_data: dict[str, pd.DataFrame] = field(default_factory=dict)
    error_message: str = ""


@dataclass(frozen=True)
class MacroDashboard:
    """Macro dashboard data package for Morning Brief."""

    indicators: list[MacroIndicator]
    updated_at: datetime
    success_count: int
    failed_count: int
    market_status: str
    macro_score: float = 50.0
    market_signal: str = "NEUTRAL"
    signal_label: str = "🟡 관망"
    histories: dict[str, pd.DataFrame] = field(default_factory=dict)

    @property
    def overview(self) -> pd.DataFrame:
        """Return indicators as a DataFrame for UI compatibility."""

        rows = []
        for item in self.indicators:
            rows.append(
                {
                    "name": item.name,
                    "ticker": item.symbol,
                    "current_value": item.value,
                    "daily_return": item.change_pct,
                    "change": item.change,
                    "currency": item.currency,
                    "status": item.status,
                    "updated_at": item.updated_at,
                    "source": item.source,
                    "success": item.status == "OK",
                    "message": item.error_message or "OK",
                }
            )
        return pd.DataFrame(rows)


@dataclass(frozen=True)
class MacroBriefResult:
    """Backward-compatible Morning Brief wrapper."""

    macro_score: float
    traffic_light: str
    market_status: str
    updated_at: datetime
    overview: pd.DataFrame
    histories: dict[str, pd.DataFrame]
    dashboard: MacroDashboard | None = None
    market_signal: str = "NEUTRAL"
