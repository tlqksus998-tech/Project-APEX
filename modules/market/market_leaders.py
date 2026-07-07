from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

try:
    from pykrx import stock
except Exception:  # pragma: no cover - optional dependency fallback
    stock = None


NASDAQ_UNIVERSE = [
    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("NVDA", "NVIDIA"),
    ("AMZN", "Amazon"),
    ("GOOGL", "Alphabet Class A"),
    ("GOOG", "Alphabet Class C"),
    ("META", "Meta Platforms"),
    ("AVGO", "Broadcom"),
    ("TSLA", "Tesla"),
    ("COST", "Costco"),
    ("NFLX", "Netflix"),
    ("AMD", "AMD"),
    ("ADBE", "Adobe"),
    ("CSCO", "Cisco"),
    ("PEP", "PepsiCo"),
    ("QCOM", "Qualcomm"),
    ("INTU", "Intuit"),
    ("AMAT", "Applied Materials"),
    ("TXN", "Texas Instruments"),
    ("MU", "Micron"),
]


@dataclass(frozen=True)
class MarketLeaderItem:
    """One market leader row."""

    rank: int
    ticker: str
    name: str
    market: str
    price: float
    change_pct: float
    market_cap: float
    trading_value: float
    currency: str
    updated_at: str
    source: str


@dataclass(frozen=True)
class MarketLeadersResult:
    """Grouped market leader dashboard result."""

    kospi_market_cap_top10: list[MarketLeaderItem]
    kospi_trading_value_top10: list[MarketLeaderItem]
    nasdaq_market_cap_top10: list[MarketLeaderItem]
    nasdaq_trading_value_top10: list[MarketLeaderItem]
    updated_at: str
    error_message: str


def get_market_leaders() -> MarketLeadersResult:
    """Return market leader groups with safe fallbacks."""

    errors: list[str] = []
    kospi_cap, error = get_kospi_market_cap_top10()
    if error:
        errors.append(error)
    kospi_value, error = get_kospi_trading_value_top10()
    if error:
        errors.append(error)
    nasdaq_cap, error = get_nasdaq_market_cap_top10()
    if error:
        errors.append(error)
    nasdaq_value, error = get_nasdaq_trading_value_top10()
    if error:
        errors.append(error)

    return MarketLeadersResult(
        kospi_market_cap_top10=kospi_cap,
        kospi_trading_value_top10=kospi_value,
        nasdaq_market_cap_top10=nasdaq_cap,
        nasdaq_trading_value_top10=nasdaq_value,
        updated_at=current_timestamp(),
        error_message=" | ".join(errors),
    )


def get_kospi_market_cap_top10() -> tuple[list[MarketLeaderItem], str]:
    """Return KOSPI top 10 by market cap using pykrx when available."""

    frame, error = load_kospi_pykrx_frame()
    if frame.empty:
        return fallback_kospi_items("market_cap"), error or "KOSPI 데이터를 가져오지 못해 샘플 데이터를 표시합니다."
    return frame_to_leaders(frame.sort_values("market_cap", ascending=False).head(10), "KOSPI", "KRW", "pykrx"), error


def get_kospi_trading_value_top10() -> tuple[list[MarketLeaderItem], str]:
    """Return KOSPI top 10 by trading value using pykrx when available."""

    frame, error = load_kospi_pykrx_frame()
    if frame.empty:
        return fallback_kospi_items("trading_value"), error or "KOSPI 데이터를 가져오지 못해 샘플 데이터를 표시합니다."
    return frame_to_leaders(frame.sort_values("trading_value", ascending=False).head(10), "KOSPI", "KRW", "pykrx"), error


def get_nasdaq_market_cap_top10() -> tuple[list[MarketLeaderItem], str]:
    """Return NASDAQ MVP top 10 by market cap from a representative universe."""

    frame = fallback_nasdaq_frame()
    return frame_to_leaders(frame.sort_values("market_cap", ascending=False).head(10), "NASDAQ", "USD", "mvp_universe"), ""


def get_nasdaq_trading_value_top10() -> tuple[list[MarketLeaderItem], str]:
    """Return NASDAQ MVP top 10 by trading value from a representative universe."""

    frame = fallback_nasdaq_frame()
    return frame_to_leaders(frame.sort_values("trading_value", ascending=False).head(10), "NASDAQ", "USD", "mvp_universe"), ""


def load_kospi_pykrx_frame() -> tuple[pd.DataFrame, str]:
    """Load KOSPI market cap and trading value data from pykrx."""

    if stock is None:
        return pd.DataFrame(), "pykrx를 사용할 수 없어 KOSPI 샘플 데이터를 표시합니다."
    try:
        date = datetime.now().strftime("%Y%m%d")
        raw = stock.get_market_cap_by_ticker(date, market="KOSPI")
        if raw is None or raw.empty:
            return pd.DataFrame(), "KOSPI 조회 결과가 비어 있어 샘플 데이터를 표시합니다."
        frame = raw.copy().reset_index().rename(columns={"티커": "ticker", "종가": "price", "시가총액": "market_cap", "거래대금": "trading_value"})
        if "ticker" not in frame.columns:
            frame = frame.rename(columns={frame.columns[0]: "ticker"})
        frame["name"] = frame["ticker"].map(safe_krx_name)
        frame["change_pct"] = 0.0
        for column in ["price", "market_cap", "trading_value"]:
            frame[column] = pd.to_numeric(frame.get(column, 0.0), errors="coerce").fillna(0.0)
        return frame[["ticker", "name", "price", "change_pct", "market_cap", "trading_value"]], ""
    except Exception as exc:
        return pd.DataFrame(), f"KOSPI 조회 실패: {exc.__class__.__name__}. 샘플 데이터를 표시합니다."


def safe_krx_name(ticker: str) -> str:
    """Resolve KRX ticker name without raising."""

    try:
        return str(stock.get_market_ticker_name(ticker)) if stock is not None else str(ticker)
    except Exception:
        return str(ticker)


def frame_to_leaders(frame: pd.DataFrame, market: str, currency: str, source: str) -> list[MarketLeaderItem]:
    """Convert a normalized DataFrame into ranked leader items."""

    rows: list[MarketLeaderItem] = []
    timestamp = current_timestamp()
    for rank, row in enumerate(frame.to_dict(orient="records"), start=1):
        rows.append(
            MarketLeaderItem(
                rank=rank,
                ticker=str(row.get("ticker", "")),
                name=str(row.get("name", "")),
                market=market,
                price=safe_float(row.get("price")),
                change_pct=safe_float(row.get("change_pct")),
                market_cap=safe_float(row.get("market_cap")),
                trading_value=safe_float(row.get("trading_value")),
                currency=currency,
                updated_at=timestamp,
                source=source,
            )
        )
    return rows


def fallback_kospi_items(sort_by: str) -> list[MarketLeaderItem]:
    """Return deterministic KOSPI fallback leader rows."""

    rows = [
        ("005930", "삼성전자", 80000, 0.3, 477000000000000, 1200000000000),
        ("000660", "SK하이닉스", 210000, 0.8, 153000000000000, 900000000000),
        ("373220", "LG에너지솔루션", 380000, -0.4, 89000000000000, 230000000000),
        ("005380", "현대차", 260000, 0.1, 55000000000000, 310000000000),
        ("035420", "NAVER", 190000, -0.2, 31000000000000, 180000000000),
        ("005490", "POSCO홀딩스", 390000, 0.5, 33000000000000, 220000000000),
        ("000270", "기아", 120000, 0.2, 48000000000000, 260000000000),
        ("068270", "셀트리온", 180000, -0.1, 39000000000000, 210000000000),
        ("035720", "카카오", 45000, 0.0, 20000000000000, 160000000000),
        ("207940", "삼성바이오로직스", 820000, 0.4, 58000000000000, 170000000000),
    ]
    frame = pd.DataFrame(rows, columns=["ticker", "name", "price", "change_pct", "market_cap", "trading_value"])
    return frame_to_leaders(frame.sort_values(sort_by, ascending=False).head(10), "KOSPI", "KRW", "fallback")


def fallback_nasdaq_frame() -> pd.DataFrame:
    """Return deterministic NASDAQ representative universe data."""

    rows = []
    base_caps = [3200, 3100, 2900, 2100, 2050, 1950, 1600, 1450, 900, 420, 390, 360, 330, 270, 260, 250, 230, 220, 190, 180]
    for index, (ticker, name) in enumerate(NASDAQ_UNIVERSE):
        price = 80.0 + index * 12.5
        market_cap = base_caps[index] * 1_000_000_000
        volume = 20_000_000 + (len(NASDAQ_UNIVERSE) - index) * 1_000_000
        rows.append(
            {
                "ticker": ticker,
                "name": name,
                "price": price,
                "change_pct": round((index % 5 - 2) * 0.35, 2),
                "market_cap": market_cap,
                "trading_value": price * volume,
            }
        )
    return pd.DataFrame(rows)


def safe_float(value: object) -> float:
    """Convert a value to float with zero fallback."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def current_timestamp() -> str:
    """Return a display timestamp."""

    return datetime.now().strftime("%Y-%m-%d %H:%M")
