from __future__ import annotations

import pandas as pd

from modules.analysis.analysis_engine import (
    STATUS_INSUFFICIENT,
    TREND_UP,
    VOLUME_DOWN,
    VOLUME_NORMAL,
    VOLUME_UP,
    analyze_ohlcv,
    analyze_volume,
    calculate_week52_position,
)
from modules.analysis.technical_indicators import calculate_macd, calculate_moving_average, calculate_rsi


def make_ohlcv(length: int = 260, volume: float = 1000.0) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=length, freq="D")
    close = pd.Series(range(100, 100 + length), dtype="float64")
    return pd.DataFrame(
        {
            "date": dates,
            "open": close - 1,
            "high": close + 1,
            "low": close - 2,
            "close": close,
            "volume": volume,
        }
    )


def test_calculate_rsi_returns_series():
    close = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], dtype="float64")
    rsi = calculate_rsi(close, period=14)

    assert len(rsi) == len(close)
    assert rsi.iloc[-1] == 100.0


def test_calculate_moving_average_returns_expected_value():
    close = pd.Series([1, 2, 3, 4, 5], dtype="float64")
    ma = calculate_moving_average(close, window=3)

    assert ma.iloc[-1] == 4.0


def test_calculate_macd_returns_expected_columns():
    close = pd.Series(range(1, 80), dtype="float64")
    macd = calculate_macd(close)

    assert list(macd.columns) == ["macd", "macd_signal", "macd_histogram"]
    assert len(macd) == len(close)
    assert pd.notna(macd.iloc[-1]["macd"])


def test_volume_status_rules():
    normal = make_ohlcv(length=25, volume=1000.0)
    latest_volume, avg_volume, ratio, status = analyze_volume(normal)
    assert latest_volume == 1000.0
    assert avg_volume == 1000.0
    assert ratio == 1.0
    assert status == VOLUME_NORMAL

    up = normal.copy()
    up.loc[up.index[-1], "volume"] = 2000.0
    assert analyze_volume(up)[3] == VOLUME_UP

    down = normal.copy()
    down.loc[down.index[-1], "volume"] = 100.0
    assert analyze_volume(down)[3] == VOLUME_DOWN


def test_week52_position_calculation():
    data = make_ohlcv(length=260)
    high, low, position = calculate_week52_position(data)

    assert high is not None
    assert low is not None
    assert position is not None
    assert 0 <= position <= 100


def test_analyze_ohlcv_success_with_normal_input():
    result = analyze_ohlcv("AAPL", make_ohlcv())

    assert result.success is True
    assert result.latest_close is not None
    assert result.rsi_14 is not None
    assert result.ma20 is not None
    assert result.ma60 is not None
    assert result.ma120 is not None
    assert result.trend_status == TREND_UP
    assert result.macd is not None
    assert result.macd_signal is not None
    assert result.macd_histogram is not None
    assert result.macd_status != STATUS_INSUFFICIENT
    assert result.volume_status == VOLUME_NORMAL
    assert result.volume_ratio == 1.0
    assert result.week52_position is not None


def test_analyze_ohlcv_fails_when_close_missing():
    data = make_ohlcv().drop(columns=["close"])
    result = analyze_ohlcv("AAPL", data)

    assert result.success is False
    assert result.trend_status == STATUS_INSUFFICIENT
    assert result.macd_status == STATUS_INSUFFICIENT
    assert result.volume_status == STATUS_INSUFFICIENT


def test_analyze_ohlcv_handles_insufficient_data():
    result = analyze_ohlcv("AAPL", make_ohlcv(length=5))

    assert result.success is True
    assert result.trend_status == STATUS_INSUFFICIENT
    assert result.ma20 is None
    assert result.macd_status == STATUS_INSUFFICIENT
    assert result.volume_status == STATUS_INSUFFICIENT
