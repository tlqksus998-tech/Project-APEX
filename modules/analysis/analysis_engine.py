from __future__ import annotations

import math

import pandas as pd

from modules.analysis.analysis_models import TechnicalAnalysisResult
from modules.analysis.technical_indicators import calculate_macd, calculate_moving_average, calculate_rsi


TREND_UP = "\uc0c1\uc2b9\ucd94\uc138"
TREND_DOWN = "\ud558\ub77d\ucd94\uc138"
STATUS_NEUTRAL = "\uc911\ub9bd"
STATUS_INSUFFICIENT = "\ub370\uc774\ud130 \ubd80\uc871"
MACD_UP = "\uc0c1\uc2b9 \ubaa8\uba58\ud140"
MACD_DOWN = "\ud558\ub77d \ubaa8\uba58\ud140"
VOLUME_UP = "\uac70\ub798\ub7c9 \uc99d\uac00"
VOLUME_NORMAL = "\uac70\ub798\ub7c9 \ubcf4\ud1b5"
VOLUME_DOWN = "\uac70\ub798\ub7c9 \uac10\uc18c"


def analyze_ohlcv(ticker: str, ohlcv: pd.DataFrame) -> TechnicalAnalysisResult:
    """Analyze normalized OHLCV data and return a compact technical result."""

    display_ticker = str(ticker or "UNKNOWN").upper().strip() or "UNKNOWN"
    if ohlcv is None or ohlcv.empty:
        return failed_result(display_ticker, "OHLCV data is empty.")
    if "close" not in ohlcv.columns:
        return failed_result(display_ticker, "OHLCV data is missing the close column.")

    frame = ohlcv.copy()
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.dropna(subset=["close"])
    if frame.empty:
        return failed_result(display_ticker, "No valid close prices are available.")

    close = frame["close"]
    rsi_14 = calculate_rsi(close, period=14)
    ma20 = calculate_moving_average(close, window=20)
    ma60 = calculate_moving_average(close, window=60)
    ma120 = calculate_moving_average(close, window=120)
    macd_frame = calculate_macd(close)

    latest_close = to_optional_float(close.iloc[-1])
    latest_rsi = last_optional_value(rsi_14)
    latest_ma20 = last_optional_value(ma20)
    latest_ma60 = last_optional_value(ma60)
    latest_ma120 = last_optional_value(ma120)
    latest_macd = last_optional_value(macd_frame["macd"]) if "macd" in macd_frame else None
    latest_macd_signal = last_optional_value(macd_frame["macd_signal"]) if "macd_signal" in macd_frame else None
    latest_macd_histogram = last_optional_value(macd_frame["macd_histogram"]) if "macd_histogram" in macd_frame else None

    latest_volume, avg_volume_20, volume_ratio, volume_status = analyze_volume(frame)
    week52_high, week52_low, week52_position = calculate_week52_position(frame)
    trend_status = determine_trend_status(latest_close, latest_ma20, latest_ma60)
    macd_status = determine_macd_status(latest_macd, latest_macd_signal, latest_macd_histogram)

    return TechnicalAnalysisResult(
        ticker=display_ticker,
        latest_close=latest_close,
        rsi_14=latest_rsi,
        ma20=latest_ma20,
        ma60=latest_ma60,
        ma120=latest_ma120,
        trend_status=trend_status,
        macd=latest_macd,
        macd_signal=latest_macd_signal,
        macd_histogram=latest_macd_histogram,
        macd_status=macd_status,
        latest_volume=latest_volume,
        avg_volume_20=avg_volume_20,
        volume_ratio=volume_ratio,
        volume_status=volume_status,
        week52_high=week52_high,
        week52_low=week52_low,
        week52_position=week52_position,
        success=True,
        message="OK" if trend_status != STATUS_INSUFFICIENT else "Not enough data for full trend analysis.",
    )


def analyze_many(histories: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Analyze multiple ticker histories and return a display-ready DataFrame."""

    results = [analyze_ohlcv(ticker, history).__dict__ for ticker, history in histories.items()]
    return pd.DataFrame(results)


def analyze_volume(frame: pd.DataFrame) -> tuple[float | None, float | None, float | None, str]:
    """Analyze recent volume versus the 20-day average volume."""

    if "volume" not in frame.columns:
        return None, None, None, STATUS_INSUFFICIENT
    volume = pd.to_numeric(frame["volume"], errors="coerce").dropna()
    if len(volume) < 20:
        return last_optional_value(volume), None, None, STATUS_INSUFFICIENT

    latest_volume = to_optional_float(volume.iloc[-1])
    avg_volume_20 = to_optional_float(volume.tail(20).mean())
    if latest_volume is None or avg_volume_20 is None or avg_volume_20 <= 0:
        return latest_volume, avg_volume_20, None, STATUS_INSUFFICIENT

    ratio = latest_volume / avg_volume_20
    if ratio >= 1.5:
        status = VOLUME_UP
    elif ratio >= 0.7:
        status = VOLUME_NORMAL
    else:
        status = VOLUME_DOWN
    return latest_volume, avg_volume_20, ratio, status


def calculate_week52_position(frame: pd.DataFrame) -> tuple[float | None, float | None, float | None]:
    """Calculate latest close location between the 52-week high and low as 0-100."""

    required = {"high", "low", "close"}
    if not required.issubset(frame.columns):
        return None, None, None

    window = frame.tail(252).copy()
    high = pd.to_numeric(window["high"], errors="coerce").dropna()
    low = pd.to_numeric(window["low"], errors="coerce").dropna()
    close = pd.to_numeric(window["close"], errors="coerce").dropna()
    if high.empty or low.empty or close.empty:
        return None, None, None

    week52_high = to_optional_float(high.max())
    week52_low = to_optional_float(low.min())
    latest_close = to_optional_float(close.iloc[-1])
    if week52_high is None or week52_low is None or latest_close is None or week52_high == week52_low:
        return week52_high, week52_low, None

    position = ((latest_close - week52_low) / (week52_high - week52_low)) * 100
    bounded_position = max(0.0, min(100.0, position))
    return week52_high, week52_low, bounded_position


def determine_trend_status(latest_close: float | None, ma20: float | None, ma60: float | None) -> str:
    """Determine a simple trend label from close, MA20, and MA60."""

    if latest_close is None or ma20 is None or ma60 is None:
        return STATUS_INSUFFICIENT
    if latest_close > ma20 > ma60:
        return TREND_UP
    if latest_close < ma20 < ma60:
        return TREND_DOWN
    return STATUS_NEUTRAL


def determine_macd_status(macd: float | None, macd_signal: float | None, macd_histogram: float | None) -> str:
    """Determine a simple MACD momentum label."""

    if macd is None or macd_signal is None or macd_histogram is None:
        return STATUS_INSUFFICIENT
    if macd > macd_signal and macd_histogram > 0:
        return MACD_UP
    if macd < macd_signal and macd_histogram < 0:
        return MACD_DOWN
    return STATUS_NEUTRAL


def failed_result(ticker: str, message: str) -> TechnicalAnalysisResult:
    """Build a failed technical analysis result."""

    return TechnicalAnalysisResult(
        ticker=ticker,
        latest_close=None,
        rsi_14=None,
        ma20=None,
        ma60=None,
        ma120=None,
        trend_status=STATUS_INSUFFICIENT,
        macd=None,
        macd_signal=None,
        macd_histogram=None,
        macd_status=STATUS_INSUFFICIENT,
        latest_volume=None,
        avg_volume_20=None,
        volume_ratio=None,
        volume_status=STATUS_INSUFFICIENT,
        week52_high=None,
        week52_low=None,
        week52_position=None,
        success=False,
        message=message,
    )


def last_optional_value(series: pd.Series) -> float | None:
    """Return the last value of a series as an optional float."""

    if series.empty:
        return None
    return to_optional_float(series.iloc[-1])


def to_optional_float(value: object) -> float | None:
    """Convert numeric values to float while preserving missing values as None."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric):
        return None
    return numeric
