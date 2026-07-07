from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

try:
    from pykrx import stock
except Exception:  # pragma: no cover
    stock = None

from modules.data_providers.provider_models import LivePriceResult
from modules.market.ticker_utils import resolve_krx_code

KST = ZoneInfo("Asia/Seoul")


def get_krx_live_price(ticker: str, name: str = "") -> LivePriceResult:
    """Fetch recent Korean stock price via pykrx with fallback."""

    code = resolve_krx_code(ticker) or str(ticker or "").strip()
    if stock is None or not code:
        return fallback_krx_price(code, name, "pykrx unavailable")
    try:
        date = datetime.now(KST).strftime("%Y%m%d")
        cap = stock.get_market_cap_by_ticker(date)
        if cap is None or cap.empty or code not in cap.index:
            return fallback_krx_price(code, name, "empty pykrx market cap")
        row = cap.loc[code]
        price = safe_float(row.get("종가"))
        market_cap = safe_float(row.get("시가총액"))
        trading_value = safe_float(row.get("거래대금"))
        volume = safe_float(row.get("거래량"))
        resolved_name = name or safe_krx_name(code)
        return LivePriceResult(code, resolved_name, "KR", price, 0.0, 0.0, volume, trading_value, market_cap, "KRW", now_kst(), "pykrx", True, False, "")
    except Exception as exc:
        return fallback_krx_price(code, name, f"pykrx error: {exc.__class__.__name__}")


def safe_krx_name(code: str) -> str:
    """Resolve KRX ticker name safely."""

    try:
        return str(stock.get_market_ticker_name(code)) if stock is not None else code
    except Exception:
        return code


def fallback_krx_price(ticker: str, name: str, error: str) -> LivePriceResult:
    """Return fallback Korean price result."""

    return LivePriceResult(ticker, name or ticker, "KR", 100000.0, 0.0, 0.0, 0.0, 0.0, 0.0, "KRW", now_kst(), "fallback", False, True, error)


def safe_float(value: object) -> float:
    """Convert value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def now_kst() -> datetime:
    """Return current KST timestamp."""

    return datetime.now(KST)
