from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

try:
    import yfinance as yf
except Exception:  # pragma: no cover
    yf = None

from modules.data_providers.provider_models import LivePriceResult, MarketIndexResult

KST = ZoneInfo("Asia/Seoul")
INDEX_TICKERS = {
    "^GSPC": "S&P500",
    "^IXIC": "NASDAQ",
    "^VIX": "VIX",
    "GC=F": "Gold",
    "CL=F": "WTI",
}


def get_us_live_price(ticker: str, name: str = "") -> LivePriceResult:
    """Fetch recent US stock price via yfinance with fallback."""

    symbol = str(ticker or "").upper().strip()
    if yf is None or not symbol:
        return fallback_price(symbol, name, "US", "USD", "yfinance unavailable")
    try:
        yf_ticker = yf.Ticker(symbol)
        history = yf_ticker.history(period="5d", interval="1d")
        price, previous, volume = extract_history(history)
        if price <= 0:
            return fallback_price(symbol, name, "US", "USD", "empty yfinance history")
        info = safe_info(yf_ticker)
        market_cap = safe_float(info.get("marketCap"))
        change = price - previous if previous > 0 else 0.0
        change_pct = change / previous if previous > 0 else 0.0
        return LivePriceResult(symbol, name or symbol, "US", price, change, change_pct, volume, price * volume, market_cap, "USD", now_kst(), "yfinance", True, False, "")
    except Exception as exc:
        return fallback_price(symbol, name, "US", "USD", f"yfinance error: {exc.__class__.__name__}")


def get_market_index(symbol: str, name: str | None = None) -> MarketIndexResult:
    """Fetch recent market index value via yfinance with fallback."""

    clean = str(symbol or "").strip()
    display_name = name or INDEX_TICKERS.get(clean, clean)
    if yf is None or not clean:
        return fallback_index(clean, display_name, "yfinance unavailable")
    try:
        history = yf.Ticker(clean).history(period="5d", interval="1d")
        value, previous, _ = extract_history(history)
        if value <= 0:
            return fallback_index(clean, display_name, "empty yfinance history")
        change = value - previous if previous > 0 else 0.0
        change_pct = change / previous if previous > 0 else 0.0
        return MarketIndexResult(clean, display_name, value, change, change_pct, now_kst(), "yfinance", True, False, "")
    except Exception as exc:
        return fallback_index(clean, display_name, f"yfinance error: {exc.__class__.__name__}")


def extract_history(history: pd.DataFrame | None) -> tuple[float, float, float]:
    """Extract latest price, previous price, and volume."""

    if history is None or history.empty or "Close" not in history.columns:
        return 0.0, 0.0, 0.0
    close = pd.to_numeric(history["Close"], errors="coerce").dropna()
    volume = pd.to_numeric(history.get("Volume", pd.Series(dtype=float)), errors="coerce").dropna()
    if close.empty:
        return 0.0, 0.0, 0.0
    latest = float(close.iloc[-1])
    previous = float(close.iloc[-2]) if len(close) > 1 else latest
    latest_volume = float(volume.iloc[-1]) if not volume.empty else 0.0
    return latest, previous, latest_volume


def safe_info(yf_ticker: object) -> dict[str, object]:
    """Read yfinance info safely."""

    try:
        value = getattr(yf_ticker, "fast_info", {}) or {}
        return dict(value)
    except Exception:
        return {}


def fallback_price(ticker: str, name: str, market: str, currency: str, error: str) -> LivePriceResult:
    """Return fallback price result."""

    price = 100.0
    return LivePriceResult(ticker, name or ticker, market, price, 0.0, 0.0, 0.0, 0.0, 0.0, currency, now_kst(), "fallback", False, True, error)


def fallback_index(symbol: str, name: str, error: str) -> MarketIndexResult:
    """Return fallback market index result."""

    return MarketIndexResult(symbol, name, 100.0, 0.0, 0.0, now_kst(), "fallback", False, True, error)


def safe_float(value: object) -> float:
    """Convert value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def now_kst() -> datetime:
    """Return current KST timestamp."""

    return datetime.now(KST)
