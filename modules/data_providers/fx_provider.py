from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

try:
    import yfinance as yf
except Exception:  # pragma: no cover
    yf = None

from modules.data_providers.provider_models import FxRateResult

KST = ZoneInfo("Asia/Seoul")
DEFAULT_USDKRW = 1380.0
FX_TICKERS = ("KRW=X", "USDKRW=X")


def get_usdkrw_rate(fallback_rate: float = DEFAULT_USDKRW) -> FxRateResult:
    """Fetch recent USD/KRW rate with fallback."""

    fallback = safe_rate(fallback_rate)
    if yf is None:
        return FxRateResult("USD/KRW", fallback, now_kst(), "fallback", False, True, "yfinance를 사용할 수 없어 기존 환율을 유지합니다.")
    for ticker in FX_TICKERS:
        try:
            history = yf.Ticker(ticker).history(period="5d", interval="1d")
            rate = latest_close(history)
            if rate > 0:
                return FxRateResult("USD/KRW", rate, now_kst(), f"yfinance:{ticker}", True, False, "")
        except Exception:
            continue
    return FxRateResult("USD/KRW", fallback, now_kst(), "fallback", False, True, "환율 조회에 실패해 기존 입력값을 유지합니다.")


def latest_close(history: pd.DataFrame | None) -> float:
    """Return latest close from a history frame."""

    if history is None or history.empty or "Close" not in history.columns:
        return 0.0
    values = pd.to_numeric(history["Close"], errors="coerce").dropna()
    return float(values.iloc[-1]) if not values.empty else 0.0


def safe_rate(value: float) -> float:
    """Return positive FX fallback."""

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return DEFAULT_USDKRW
    return parsed if parsed > 0 else DEFAULT_USDKRW


def now_kst() -> datetime:
    """Return current KST timestamp."""

    return datetime.now(KST)
