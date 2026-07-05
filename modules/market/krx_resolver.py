from __future__ import annotations

from functools import lru_cache

import pandas as pd

try:
    from pykrx import stock
except Exception:  # pragma: no cover - optional dependency fallback
    stock = None


SAMSUNG_ELECTRONICS = "\uc0bc\uc131\uc804\uc790"
SK_HYNIX = "SK\ud558\uc774\ub2c9\uc2a4"
HYUNDAI_MOTOR = "\ud604\ub300\ucc28"
KAKAO = "\uce74\uce74\uc624"
LG_ENERGY = "LG\uc5d0\ub108\uc9c0\uc194\ub8e8\uc158"
POSCO_HOLDINGS = "POSCO\ud640\ub529\uc2a4"
MIRAE_VENTURE = "\ubbf8\ub798\uc5d0\uc14b\ubca4\ucc98\ud22c\uc790"
NEXON_GAMES = "\ub125\uc2a8\uac8c\uc784\uc988"
TIGER_US_SP500 = "TIGER \ubbf8\uad6dS&P500"
SAMSUNG_SDI = "\uc0bc\uc131SDI"
SAMSUNG_BIO = "\uc0bc\uc131\ubc14\uc774\uc624\ub85c\uc9c1\uc2a4"

FALLBACK_KRX_NAME_TO_TICKER = {
    SAMSUNG_ELECTRONICS: "005930",
    SK_HYNIX: "000660",
    HYUNDAI_MOTOR: "005380",
    "NAVER": "035420",
    KAKAO: "035720",
    LG_ENERGY: "373220",
    POSCO_HOLDINGS: "005490",
    MIRAE_VENTURE: "100790",
    NEXON_GAMES: "225570",
    TIGER_US_SP500: "360750",
    SAMSUNG_SDI: "006400",
    SAMSUNG_BIO: "207940",
}

FALLBACK_KRX_TICKER_TO_NAME = {ticker: name for name, ticker in FALLBACK_KRX_NAME_TO_TICKER.items()}
ETF_BRANDS = ("TIGER", "KODEX", "ACE", "KOSEF", "SOL", "RISE", "HANARO", "PLUS")


@lru_cache(maxsize=1)
def get_krx_listing() -> pd.DataFrame:
    """Return KRX ticker/name listing with pykrx when available and fallback rows always included."""

    rows: list[dict[str, str]] = []
    if stock is not None:
        try:
            tickers = stock.get_market_ticker_list(market="ALL")
            for ticker in tickers:
                name = stock.get_market_ticker_name(ticker)
                if name:
                    rows.append({"ticker": str(ticker), "name": str(name)})
        except Exception:
            rows = []

    for name, ticker in FALLBACK_KRX_NAME_TO_TICKER.items():
        rows.append({"ticker": ticker, "name": name})

    frame = pd.DataFrame(rows).drop_duplicates(subset=["ticker"], keep="last")
    frame["ticker"] = frame["ticker"].astype(str).str.zfill(6)
    frame["name"] = frame["name"].astype(str)
    return frame.reset_index(drop=True)


def krx_name_to_ticker(name: str) -> str | None:
    """Resolve a Korean stock or ETF name to a six-digit KRX ticker."""

    query = normalize_name(name)
    if not query:
        return None

    fallback = {normalize_name(key): value for key, value in FALLBACK_KRX_NAME_TO_TICKER.items()}
    if query in fallback:
        return fallback[query]

    listing = get_krx_listing()
    exact = listing[listing["name"].map(normalize_name) == query]
    if not exact.empty:
        return str(exact.iloc[0]["ticker"])
    return None


def krx_ticker_to_name(ticker: str) -> str | None:
    """Resolve a six-digit KRX ticker to a stock or ETF name."""

    code = str(ticker or "").strip().replace(".KS", "").replace(".KQ", "").zfill(6)
    if code in FALLBACK_KRX_TICKER_TO_NAME:
        return FALLBACK_KRX_TICKER_TO_NAME[code]

    listing = get_krx_listing()
    match = listing[listing["ticker"] == code]
    if not match.empty:
        return str(match.iloc[0]["name"])
    return None


def suggest_krx_names(query: str, limit: int = 10) -> list[str]:
    """Suggest KRX names containing the user's partial query."""

    normalized_query = normalize_name(query)
    if not normalized_query:
        return []

    listing = get_krx_listing()
    mask = listing["name"].map(normalize_name).str.contains(normalized_query, regex=False, na=False)
    return listing.loc[mask, "name"].head(limit).tolist()


def is_known_krx_name(value: str) -> bool:
    """Return True when a user input resolves as a KRX stock or ETF name."""

    return krx_name_to_ticker(value) is not None


def is_korean_etf_name(value: str) -> bool:
    """Return True when a name begins with a supported Korean ETF brand."""

    normalized = normalize_name(value).upper()
    return any(normalized.startswith(brand) for brand in ETF_BRANDS)


def normalize_name(value: str) -> str:
    """Normalize Korean/English instrument names for lookup."""

    return "".join(str(value or "").strip().split()).upper()
