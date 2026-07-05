from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from modules.portfolio.input_data import PORTFOLIO_COLUMNS, normalize_portfolio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PORTFOLIO_PATH = PROJECT_ROOT / "data" / "portfolio" / "portfolio.json"
SCHEMA_VERSION = 1
FRIENDLY_INVALID_JSON = "\ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ud30c\uc77c \ud615\uc2dd\uc774 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4."


def get_default_portfolio_path() -> Path:
    """Return the default local portfolio JSON path."""

    return DEFAULT_PORTFOLIO_PATH


def build_portfolio_payload(portfolio: pd.DataFrame | None) -> dict[str, object]:
    """Build the portable JSON payload for a portfolio."""

    cleaned = normalize_portfolio(portfolio)
    return {"schema_version": SCHEMA_VERSION, "holdings": cleaned[PORTFOLIO_COLUMNS].to_dict(orient="records")}


def portfolio_to_json_bytes(portfolio: pd.DataFrame | None) -> tuple[bytes | None, str | None]:
    """Convert a portfolio to downloadable JSON bytes."""

    try:
        cleaned = normalize_portfolio(portfolio)
        if cleaned.empty:
            return None, "\ub2e4\uc6b4\ub85c\ub4dc\ud560 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\uac00 \uc5c6\uc2b5\ub2c8\ub2e4."
        payload = build_portfolio_payload(cleaned)
        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"), None
    except Exception:
        return None, "Portfolio download data could not be created."


def validate_portfolio_payload(payload: object) -> tuple[pd.DataFrame, str | None]:
    """Validate uploaded portfolio JSON payload and return normalized holdings."""

    if not isinstance(payload, dict):
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS), FRIENDLY_INVALID_JSON
    if "schema_version" not in payload or "holdings" not in payload:
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS), FRIENDLY_INVALID_JSON
    holdings = payload.get("holdings")
    if not isinstance(holdings, list):
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS), FRIENDLY_INVALID_JSON
    for holding in holdings:
        if not isinstance(holding, dict) or not set(PORTFOLIO_COLUMNS).issubset(holding.keys()):
            return pd.DataFrame(columns=PORTFOLIO_COLUMNS), FRIENDLY_INVALID_JSON
    return normalize_portfolio(pd.DataFrame(holdings, columns=PORTFOLIO_COLUMNS)), None


def load_portfolio_json_bytes(content: bytes) -> tuple[pd.DataFrame, str | None]:
    """Load a portfolio from uploaded JSON bytes."""

    try:
        payload = json.loads(content.decode("utf-8"))
    except Exception:
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS), FRIENDLY_INVALID_JSON
    return validate_portfolio_payload(payload)


def save_portfolio_json(portfolio: pd.DataFrame | None, path: Path | None = None) -> tuple[bool, str]:
    """Save a portfolio DataFrame to JSON with friendly error handling."""

    target = path or DEFAULT_PORTFOLIO_PATH
    try:
        payload = build_portfolio_payload(portfolio)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True, f"Portfolio saved to {target}."
    except Exception:
        return False, "Portfolio save failed. Please check file permissions or try again later."


def load_portfolio_json(path: Path | None = None) -> tuple[pd.DataFrame, str | None]:
    """Load a portfolio DataFrame from JSON with safe fallback."""

    target = path or DEFAULT_PORTFOLIO_PATH
    if not target.exists():
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS), "No saved portfolio file was found."
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS), "Portfolio load failed. The saved file may be damaged."
    loaded, error = validate_portfolio_payload(payload)
    if error:
        return loaded, "Portfolio load failed. The saved file may be damaged."
    return loaded, None


def delete_saved_portfolio(path: Path | None = None) -> tuple[bool, str]:
    """Delete the saved portfolio file if it exists."""

    target = path or DEFAULT_PORTFOLIO_PATH
    try:
        if target.exists():
            target.unlink()
            return True, "Saved portfolio file deleted."
        return True, "No saved portfolio file exists."
    except Exception:
        return False, "Saved portfolio could not be deleted. Please check file permissions."
