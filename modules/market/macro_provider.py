from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from modules.market.cache import cached_yfinance_history
from modules.market.macro_models import MacroBriefResult, MacroDashboard, MacroIndicator
from modules.market.macro_signal import calculate_apex_macro_score, classify_market_signal

KST = ZoneInfo("Asia/Seoul")

MACRO_INSTRUMENTS = {
    "KOSPI": {"symbol": "^KS11", "currency": "KRW"},
    "KOSDAQ": {"symbol": "^KQ11", "currency": "KRW"},
    "S&P500": {"symbol": "^GSPC", "currency": "USD"},
    "NASDAQ": {"symbol": "^IXIC", "currency": "USD"},
    "VIX": {"symbol": "^VIX", "currency": "Index"},
    "USD/KRW": {"symbol": "KRW=X", "currency": "KRW"},
    "Gold": {"symbol": "GC=F", "currency": "USD"},
    "WTI": {"symbol": "CL=F", "currency": "USD"},
}

CHART_INSTRUMENTS = ["KOSPI", "S&P500", "NASDAQ", "USD/KRW"]


def build_macro_dashboard() -> MacroDashboard:
    """Build a full macro dashboard with 1M and 6M chart data."""

    indicators = [fetch_macro_indicator(name, meta["symbol"], meta["currency"]) for name, meta in MACRO_INSTRUMENTS.items()]
    score = calculate_apex_macro_score(indicators)
    signal, label, status_message = classify_market_signal(score)
    histories = {indicator.name: indicator.chart_data.get("1mo", pd.DataFrame()) for indicator in indicators}
    return MacroDashboard(
        indicators=indicators,
        updated_at=datetime.now(KST),
        success_count=sum(1 for item in indicators if item.status == "OK"),
        failed_count=sum(1 for item in indicators if item.status != "OK"),
        market_status=status_message,
        macro_score=score,
        market_signal=signal,
        signal_label=label,
        histories=histories,
    )


def build_macro_brief(period: str = "3mo", interval: str = "1d") -> MacroBriefResult:
    """Build a backward-compatible Morning Brief result."""

    dashboard = build_macro_dashboard()
    return MacroBriefResult(
        macro_score=dashboard.macro_score,
        traffic_light=dashboard.signal_label,
        market_status=dashboard.market_status,
        updated_at=dashboard.updated_at,
        overview=dashboard.overview,
        histories=dashboard.histories,
        dashboard=dashboard,
        market_signal=dashboard.market_signal,
    )


def fetch_macro_indicator(name: str, symbol: str, currency: str) -> MacroIndicator:
    """Fetch one macro indicator with safe fallback data."""

    updated_at = datetime.now(KST)
    error_message = ""
    chart_1m = pd.DataFrame()
    chart_6m = pd.DataFrame()
    source = "yfinance"
    status = "OK"

    try:
        chart_1m = normalize_history(cached_yfinance_history(symbol, "1mo", "1d"))
        chart_6m = normalize_history(cached_yfinance_history(symbol, "6mo", "1d"))
        if chart_1m.empty and not chart_6m.empty:
            chart_1m = chart_6m.tail(22).reset_index(drop=True)
        if chart_6m.empty and not chart_1m.empty:
            chart_6m = chart_1m.copy()
        if chart_1m.empty:
            raise ValueError("Empty macro history")
    except Exception as exc:
        status = "조회 실패"
        source = "fallback"
        error_message = f"{exc.__class__.__name__}: fallback data returned"
        chart_1m = build_fallback_history(name, periods=22)
        chart_6m = build_fallback_history(name, periods=126)

    value, change, change_pct = calculate_latest_change(chart_1m)
    return MacroIndicator(
        symbol=symbol,
        name=name,
        value=value,
        change=change,
        change_pct=change_pct,
        currency=currency,
        status=status,
        updated_at=updated_at,
        source=source,
        chart_data={"1mo": chart_1m, "6mo": chart_6m},
        error_message=error_message,
    )


def fetch_macro_instrument(name: str, ticker: str, period: str, interval: str) -> tuple[object, pd.DataFrame]:
    """Backward-compatible fetch helper used by older tests."""

    indicator = fetch_macro_indicator(name, ticker, currency_for_name(name))
    history = indicator.chart_data.get("1mo", pd.DataFrame())
    result = type(
        "MacroMarketResult",
        (),
        {
            "name": indicator.name,
            "ticker": indicator.symbol,
            "current_value": indicator.value,
            "daily_return": indicator.change_pct,
            "source": indicator.source,
            "success": indicator.status == "OK",
            "updated_at": indicator.updated_at,
            "message": indicator.error_message or "OK",
        },
    )()
    return result, history


def normalize_history(raw: pd.DataFrame | None) -> pd.DataFrame:
    """Normalize yfinance history into date/close columns for charts."""

    if raw is None or raw.empty or "Close" not in raw.columns:
        return pd.DataFrame(columns=["date", "close"])
    frame = raw.reset_index().copy()
    date_column = "Date" if "Date" in frame.columns else frame.columns[0]
    frame = frame.rename(columns={date_column: "date", "Close": "close"})
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame[["date", "close"]].dropna().copy()
    return frame.reset_index(drop=True)


def calculate_latest_change(history: pd.DataFrame) -> tuple[float, float, float]:
    """Return latest value, absolute change, and percentage change."""

    if history is None or history.empty:
        return 0.0, 0.0, 0.0
    latest = float(history.iloc[-1]["close"])
    previous = float(history.iloc[-2]["close"] if len(history) > 1 else history.iloc[-1]["close"])
    change = latest - previous
    change_pct = change / previous if previous > 0 else 0.0
    return latest, change, change_pct


def build_fallback_history(name: str, periods: int = 40) -> pd.DataFrame:
    """Build deterministic fallback macro chart data."""

    base_values = {
        "KOSPI": 2850.0,
        "KOSDAQ": 850.0,
        "S&P500": 5500.0,
        "NASDAQ": 18000.0,
        "USD/KRW": 1380.0,
        "VIX": 16.0,
        "Gold": 2350.0,
        "WTI": 78.0,
    }
    base = base_values.get(name, 100.0)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=periods, freq="B")
    values = [base * (1 + (idx - periods / 2) * 0.0015) for idx in range(periods)]
    return pd.DataFrame({"date": dates, "close": values})


def calculate_macro_score(overview: pd.DataFrame) -> float:
    """Backward-compatible score helper for existing tests."""

    if overview is None or overview.empty:
        return 50.0
    indicators = []
    for _, row in overview.iterrows():
        indicators.append(
            MacroIndicator(
                symbol=str(row.get("ticker", "")),
                name=str(row.get("name", "")),
                value=float(row.get("current_value", 0.0) or 0.0),
                change=float(row.get("change", 0.0) or 0.0),
                change_pct=float(row.get("daily_return", 0.0) or 0.0),
                currency="",
                status="OK" if bool(row.get("success", True)) else "조회 실패",
                updated_at=datetime.now(KST),
                source=str(row.get("source", "")),
            )
        )
    return calculate_apex_macro_score(indicators)


def classify_macro_score(score: float) -> tuple[str, str]:
    """Backward-compatible signal label helper."""

    _, label, message = classify_market_signal(score)
    return label, message


def currency_for_name(name: str) -> str:
    """Return display currency for a known macro name."""

    meta = MACRO_INSTRUMENTS.get(name, {})
    return str(meta.get("currency", ""))
