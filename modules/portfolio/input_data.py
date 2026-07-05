from __future__ import annotations

import pandas as pd

from modules.market.ticker_utils import display_name, resolve_input_symbol, resolve_krx_code, resolve_us_alias


PORTFOLIO_COLUMNS = ["name", "ticker", "quantity", "avg_price"]


def get_sample_portfolio() -> pd.DataFrame:
    """Return sample portfolio data with Korean and US examples."""

    return pd.DataFrame(
        [
            {"name": "SK\ud558\uc774\ub2c9\uc2a4", "ticker": "SK\ud558\uc774\ub2c9\uc2a4", "quantity": 1.0, "avg_price": 180000.0},
            {"name": "KORU", "ticker": "KORU", "quantity": 1.0, "avg_price": 10.0},
            {"name": "\ub9c8\uc774\ud06c\ub860", "ticker": "\ub9c8\uc774\ud06c\ub860", "quantity": 1.0, "avg_price": 100.0},
            {"name": "\ubbf8\ub798\uc5d0\uc14b\ubca4\ucc98\ud22c\uc790", "ticker": "\ubbf8\ub798\uc5d0\uc14b\ubca4\ucc98\ud22c\uc790", "quantity": 1.0, "avg_price": 6000.0},
            {"name": "\ub125\uc2a8\uac8c\uc784\uc988", "ticker": "\ub125\uc2a8\uac8c\uc784\uc988", "quantity": 1.0, "avg_price": 15000.0},
            {"name": "TIGER \ubbf8\uad6dS&P500", "ticker": "TIGER \ubbf8\uad6dS&P500", "quantity": 1.0, "avg_price": 20000.0},
        ],
        columns=PORTFOLIO_COLUMNS,
    )


def normalize_portfolio(portfolio: pd.DataFrame | None) -> pd.DataFrame:
    """Normalize user-edited portfolio data into the app schema."""

    if portfolio is None or portfolio.empty:
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS)

    cleaned = portfolio.copy()
    for column in PORTFOLIO_COLUMNS:
        if column not in cleaned.columns:
            cleaned[column] = None

    cleaned = cleaned[PORTFOLIO_COLUMNS].copy()
    cleaned["name"] = cleaned["name"].fillna("").astype(str).str.strip()
    cleaned["ticker"] = cleaned["ticker"].fillna("").astype(str).str.strip()
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce").fillna(0.0)
    cleaned["avg_price"] = pd.to_numeric(cleaned["avg_price"], errors="coerce").fillna(0.0)
    cleaned = cleaned[(cleaned["name"] != "") | (cleaned["ticker"] != "")]
    cleaned["ticker"] = cleaned.apply(resolve_input_ticker, axis=1)
    cleaned["name"] = cleaned.apply(resolve_input_name, axis=1)
    return cleaned.reset_index(drop=True)


def resolve_input_ticker(row: pd.Series) -> str:
    """Resolve ticker from ticker field first, then name field."""

    raw_ticker = str(row.get("ticker") or "").strip()
    raw_name = str(row.get("name") or "").strip()
    for candidate in [raw_ticker, raw_name]:
        code = resolve_krx_code(candidate)
        if code:
            return code
        us_alias = resolve_us_alias(candidate)
        if us_alias:
            return us_alias
        resolved = resolve_input_symbol(candidate)
        if resolved:
            return resolved[1]
        if candidate:
            return candidate.upper()
    return ""


def resolve_input_name(row: pd.Series) -> str:
    """Resolve display name from known KRX code/name or US alias when possible."""

    raw_name = str(row.get("name") or "").strip()
    raw_ticker = str(row.get("ticker") or "").strip()
    return display_name(raw_name or raw_ticker)


def validate_portfolio(portfolio: pd.DataFrame | None) -> tuple[pd.DataFrame, list[str]]:
    """Validate portfolio rows and return valid rows plus warnings."""

    cleaned = normalize_portfolio(portfolio)
    errors: list[str] = []

    if cleaned.empty:
        errors.append("Portfolio is empty. Add at least one holding.")
        return cleaned, errors

    invalid_ticker = cleaned["ticker"] == ""
    if invalid_ticker.any():
        errors.append("Some rows have an empty ticker or unresolved name.")

    invalid_quantity = cleaned["quantity"] <= 0
    if invalid_quantity.any():
        errors.append("Quantity must be greater than zero.")

    invalid_average_price = cleaned["avg_price"] < 0
    if invalid_average_price.any():
        errors.append("Average price cannot be negative.")

    valid = cleaned[~(invalid_ticker | invalid_quantity | invalid_average_price)].copy()
    return valid.reset_index(drop=True), errors
