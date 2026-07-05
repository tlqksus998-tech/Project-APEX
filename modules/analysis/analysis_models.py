from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TechnicalAnalysisResult:
    """Technical analysis summary for one ticker."""

    ticker: str
    latest_close: float | None
    rsi_14: float | None
    ma20: float | None
    ma60: float | None
    ma120: float | None
    trend_status: str
    macd: float | None
    macd_signal: float | None
    macd_histogram: float | None
    macd_status: str
    latest_volume: float | None
    avg_volume_20: float | None
    volume_ratio: float | None
    volume_status: str
    week52_high: float | None
    week52_low: float | None
    week52_position: float | None
    success: bool
    message: str
