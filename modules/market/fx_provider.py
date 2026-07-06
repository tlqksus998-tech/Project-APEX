from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

try:
    import yfinance as yf
except Exception:  # pragma: no cover - optional dependency fallback
    yf = None

KST = ZoneInfo("Asia/Seoul")
DEFAULT_USDKRW = 1380.0
FX_TICKERS = ("KRW=X", "USDKRW=X")


@dataclass(frozen=True)
class FxRateResult:
    """USD/KRW exchange-rate fetch result."""

    pair: str
    rate: float
    source: str
    success: bool
    updated_at: datetime
    message: str


def get_usdkrw_rate(fallback_rate: float = DEFAULT_USDKRW) -> FxRateResult:
    """Fetch USD/KRW rate with a safe fallback result."""

    fallback = safe_rate(fallback_rate)
    timestamp = datetime.now(KST)
    if yf is None:
        return FxRateResult("USD/KRW", fallback, "fallback", False, timestamp, "환율 데이터를 가져올 수 없어 기존 값을 유지합니다.")

    for ticker in FX_TICKERS:
        try:
            history = yf.Ticker(ticker).history(period="5d", interval="1d")
            rate = extract_latest_close(history)
            if rate > 0:
                return FxRateResult("USD/KRW", rate, f"yfinance:{ticker}", True, datetime.now(KST), "환율을 최신 값으로 갱신했습니다.")
        except Exception:
            continue
    return FxRateResult("USD/KRW", fallback, "fallback", False, timestamp, "환율 최신화에 실패했습니다. 기존 입력값을 유지합니다.")


def extract_latest_close(history: pd.DataFrame | None) -> float:
    """Extract latest close from a yfinance history frame."""

    if history is None or history.empty or "Close" not in history.columns:
        return 0.0
    close = pd.to_numeric(history["Close"], errors="coerce").dropna()
    if close.empty:
        return 0.0
    return float(close.iloc[-1])


def safe_rate(value: float) -> float:
    """Return a positive FX rate with default fallback."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return DEFAULT_USDKRW
    return numeric if numeric > 0 else DEFAULT_USDKRW
