from __future__ import annotations

import pandas as pd


def calculate_rsi(close_prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI for a close-price series with safe fallback behavior."""

    close = pd.to_numeric(close_prices, errors="coerce")
    if close.empty or period <= 0:
        return pd.Series(index=close.index, dtype="float64")

    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    average_gain = gains.rolling(window=period, min_periods=period).mean()
    average_loss = losses.rolling(window=period, min_periods=period).mean()
    relative_strength = average_gain / average_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + relative_strength))

    no_loss = (average_loss == 0) & (average_gain > 0)
    flat = (average_loss == 0) & (average_gain == 0)
    rsi = rsi.mask(no_loss, 100.0)
    rsi = rsi.mask(flat, 50.0)
    return rsi.astype("float64")


def calculate_moving_average(close_prices: pd.Series, window: int) -> pd.Series:
    """Calculate a simple moving average for a close-price series."""

    close = pd.to_numeric(close_prices, errors="coerce")
    if close.empty or window <= 0:
        return pd.Series(index=close.index, dtype="float64")
    return close.rolling(window=window, min_periods=window).mean().astype("float64")


def calculate_macd(
    close_prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """Calculate MACD, signal, and histogram columns with safe fallback behavior."""

    close = pd.to_numeric(close_prices, errors="coerce")
    result = pd.DataFrame(index=close.index, columns=["macd", "macd_signal", "macd_histogram"], dtype="float64")
    if close.empty or min(fast_period, slow_period, signal_period) <= 0:
        return result

    ema_fast = close.ewm(span=fast_period, adjust=False, min_periods=fast_period).mean()
    ema_slow = close.ewm(span=slow_period, adjust=False, min_periods=slow_period).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal_period, adjust=False, min_periods=signal_period).mean()
    result["macd"] = macd
    result["macd_signal"] = macd_signal
    result["macd_histogram"] = macd - macd_signal
    return result.astype("float64")
