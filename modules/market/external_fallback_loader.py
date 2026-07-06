from __future__ import annotations

from io import StringIO

import pandas as pd
import requests

from modules.market.krx_resolver import normalize_name

EXTERNAL_FALLBACK_COLUMNS = ["ticker", "name", "english_name", "market", "asset_type", "source", "aliases"]

# Bootstrap rows keep newly listed or special KRX short codes searchable when
# pykrx or external listing feeds lag behind. They are merged through the same
# fallback-master pipeline as fetched external rows, not through UI search code.
BOOTSTRAP_EXTERNAL_ROWS = [
    {
        "ticker": "0126Z0",
        "name": "\uc0bc\uc131\uc5d0\ud53c\uc2a4\ud640\ub529\uc2a4",
        "english_name": "Samsung Epis Holdings",
        "market": "KOSPI",
        "asset_type": "Stock",
        "source": "external_bootstrap",
        "aliases": "Samsung Epis Holdings \uc0bc\uc131\uc5d0\ud53c\uc2a4",
    },
]

EXTERNAL_MASTER_URLS = [
    # Operators may point these to KRX listing-disclosure exports or trusted
    # quote-vendor CSVs with ticker/name/market columns. The loader is tolerant
    # of missing columns and silently falls back to existing cache/bootstrap rows.
]


def normalize_krx_short_code(value: str) -> str:
    """Normalize KRX short codes, preserving alphanumeric six-character codes."""

    code = str(value or "").strip().upper().replace(".KS", "").replace(".KQ", "")
    if not code:
        return ""
    if code.isdigit() and len(code) <= 6:
        return code.zfill(6)
    return code


def is_krx_short_code(value: str) -> bool:
    """Return True for KRX six-character numeric or alphanumeric short codes."""

    code = normalize_krx_short_code(value)
    return len(code) == 6 and code.isalnum() and any(char.isdigit() for char in code)


def load_external_fallback_master(timeout: int = 8) -> pd.DataFrame:
    """Load KRX fallback master rows from external feeds plus bootstrap rows."""

    frames = [pd.DataFrame(BOOTSTRAP_EXTERNAL_ROWS)]
    for url in EXTERNAL_MASTER_URLS:
        fetched = fetch_external_master_csv(url, timeout=timeout)
        if not fetched.empty:
            frames.append(fetched)
    return normalize_external_master(pd.concat(frames, ignore_index=True))


def fetch_external_master_csv(url: str, timeout: int = 8) -> pd.DataFrame:
    """Fetch a CSV-like external master feed in a defensive way."""

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception:
        return pd.DataFrame(columns=EXTERNAL_FALLBACK_COLUMNS)


def normalize_external_master(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize external fallback rows to the canonical market master schema."""

    if data is None or data.empty:
        return pd.DataFrame(columns=EXTERNAL_FALLBACK_COLUMNS + ["search_text"])
    frame = data.copy()
    aliases = {
        "code": "ticker",
        "short_code": "ticker",
        "symbol": "ticker",
        "isin_short_code": "ticker",
        "corp_name": "name",
        "company_name": "name",
        "issue_name": "name",
        "product_name": "name",
    }
    frame = frame.rename(columns={key: value for key, value in aliases.items() if key in frame.columns})
    for column in EXTERNAL_FALLBACK_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    frame = frame[EXTERNAL_FALLBACK_COLUMNS].copy()
    for column in EXTERNAL_FALLBACK_COLUMNS:
        frame[column] = frame[column].fillna("").astype(str).str.strip()
    frame["ticker"] = frame["ticker"].map(normalize_krx_short_code)
    frame = frame[frame["ticker"].map(is_krx_short_code)]
    frame.loc[frame["market"] == "", "market"] = "KRX"
    frame.loc[frame["asset_type"] == "", "asset_type"] = "Stock"
    frame.loc[frame["source"] == "", "source"] = "external_fallback"
    frame["search_text"] = frame.apply(build_external_search_text, axis=1)
    return frame.drop_duplicates(subset=["ticker", "market"], keep="last").reset_index(drop=True)


def build_external_search_text(row: pd.Series) -> str:
    """Build normalized search text for external fallback instruments."""

    values = [row.get("ticker", ""), row.get("name", ""), row.get("english_name", ""), row.get("aliases", "")]
    return " ".join(normalize_name(str(value)) for value in values if str(value or "").strip())
