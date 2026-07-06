from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging

import pandas as pd

try:
    from pykrx import stock
except Exception:  # pragma: no cover - optional dependency fallback
    stock = None

from modules.config import AppConfig
from modules.market.cache import cached_yfinance_history
from modules.market.market_models import MarketDataRequest, OHLCVDataResult
from modules.market.ticker_utils import display_name, display_ticker, infer_market, resolve_krx_code, to_yfinance_ticker


logger = logging.getLogger(__name__)
STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def get_ohlcv(request: MarketDataRequest, config: AppConfig) -> OHLCVDataResult:
    """Fetch OHLCV data with pykrx for Korea and yfinance fallback for all markets."""

    display = display_ticker(request.ticker)
    market = infer_market(request.ticker, request.market_hint)

    if market == "KR":
        pykrx_result = get_ohlcv_from_pykrx(request, config)
        if pykrx_result.success:
            return pykrx_result

    return get_ohlcv_from_yfinance(request, config, previous_market=market, previous_display=display)


def get_ohlcv_from_yfinance(
    request: MarketDataRequest,
    config: AppConfig,
    previous_market: str | None = None,
    previous_display: str | None = None,
) -> OHLCVDataResult:
    """Fetch OHLCV data from yfinance and return sample data on failure."""

    display = previous_display or display_ticker(request.ticker)
    yf_ticker = to_yfinance_ticker(request.ticker, request.market_hint)
    market = previous_market or infer_market(request.ticker, request.market_hint)
    if not yf_ticker:
        data = build_sample_ohlcv(display or "UNKNOWN", config)
        return OHLCVDataResult(display, display, market, data, "sample", False, "Invalid ticker. Sample data returned.")

    try:
        raw = cached_yfinance_history(yf_ticker, request.period or "6mo", request.interval or "1d")
        data = normalize_yfinance_ohlcv(raw)
        if data.empty:
            logger.info("Empty OHLCV data for %s", yf_ticker)
            data = build_sample_ohlcv(display, config)
            return OHLCVDataResult(yf_ticker, display, market, data, "sample", False, "No market data. Sample data returned.")
        return OHLCVDataResult(yf_ticker, display, market, data, "yfinance", True, "OK")
    except Exception as exc:
        logger.exception("OHLCV fetch failed for %s", yf_ticker)
        data = build_sample_ohlcv(display, config)
        return OHLCVDataResult(yf_ticker, display, market, data, "sample", False, f"Provider error: {exc.__class__.__name__}")


def get_ohlcv_from_pykrx(request: MarketDataRequest, config: AppConfig) -> OHLCVDataResult:
    """Fetch Korean OHLCV data through pykrx when available."""

    code = resolve_krx_code(request.ticker)
    display = code or display_ticker(request.ticker)
    if not code or stock is None:
        data = build_sample_ohlcv(display or "UNKNOWN", config)
        return OHLCVDataResult(display, display, "KR", data, "sample", False, "pykrx unavailable or KRX code not found.")

    try:
        end = datetime.now(UTC).strftime("%Y%m%d")
        start = (datetime.now(UTC) - timedelta(days=220)).strftime("%Y%m%d")
        raw = stock.get_market_ohlcv_by_date(start, end, code)
        data = normalize_pykrx_ohlcv(raw)
        if data.empty:
            data = build_sample_ohlcv(display, config)
            return OHLCVDataResult(code, display, "KR", data, "sample", False, "No pykrx market data. Sample data returned.")
        return OHLCVDataResult(code, display, "KR", data, "pykrx", True, "OK")
    except Exception as exc:
        logger.exception("pykrx OHLCV fetch failed for %s", code)
        data = build_sample_ohlcv(display, config)
        return OHLCVDataResult(code, display, "KR", data, "sample", False, f"pykrx error: {exc.__class__.__name__}")


def normalize_yfinance_ohlcv(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize yfinance data to date/open/high/low/close/volume columns."""

    if raw is None or raw.empty or "Close" not in raw.columns:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    frame = raw.copy().reset_index()
    date_column = "Date" if "Date" in frame.columns else frame.columns[0]
    frame = frame.rename(columns={date_column: "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    return normalize_standard_ohlcv(frame)


def normalize_pykrx_ohlcv(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize pykrx Korean OHLCV data to standard columns."""

    if raw is None or raw.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    frame = raw.copy().reset_index()
    frame = frame.rename(columns={"\ub0a0\uc9dc": "date", "\uc2dc\uac00": "open", "\uace0\uac00": "high", "\uc800\uac00": "low", "\uc885\uac00": "close", "\uac70\ub798\ub7c9": "volume"})
    return normalize_standard_ohlcv(frame)


def normalize_standard_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize an already roughly mapped OHLCV frame to standard columns."""

    for column in STANDARD_COLUMNS:
        if column not in frame.columns:
            frame[column] = 0.0 if column != "date" else pd.NaT

    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.tz_localize(None)
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)

    frame = frame.dropna(subset=["date"])
    frame = frame[frame["close"] > 0].copy()
    return frame[STANDARD_COLUMNS].reset_index(drop=True)


def normalize_ohlcv(raw: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible yfinance normalizer."""

    return normalize_yfinance_ohlcv(raw)


def build_sample_ohlcv(ticker: str, config: AppConfig) -> pd.DataFrame:
    """Build deterministic sample OHLCV data for empty or failed provider calls."""

    days = max(2, config.market_dummy_days)
    end_date = datetime.now(UTC).date()
    base_price = float(config.dummy_price)
    rows: list[dict[str, object]] = []
    for index in range(days):
        close = base_price * (1 + (index / max(days - 1, 1)) * 0.02)
        rows.append(
            {
                "date": pd.Timestamp(end_date - timedelta(days=days - index - 1)),
                "open": close * 0.995,
                "high": close * 1.01,
                "low": close * 0.99,
                "close": close,
                "volume": 0.0,
            }
        )
    return pd.DataFrame(rows, columns=STANDARD_COLUMNS)
