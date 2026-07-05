from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from modules.portfolio.input_data import PORTFOLIO_COLUMNS, normalize_portfolio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PORTFOLIO_PATH = PROJECT_ROOT / "data" / "portfolio" / "portfolio.json"


def get_default_portfolio_path() -> Path:
    """Return the default local portfolio JSON path."""

    return DEFAULT_PORTFOLIO_PATH


def save_portfolio_json(portfolio: pd.DataFrame | None, path: Path | None = None) -> tuple[bool, str]:
    """Save a portfolio DataFrame to JSON with friendly error handling."""

    target = path or DEFAULT_PORTFOLIO_PATH
    try:
        cleaned = normalize_portfolio(portfolio)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "holdings": cleaned[PORTFOLIO_COLUMNS].to_dict(orient="records"),
        }
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
        holdings = payload.get("holdings", []) if isinstance(payload, dict) else []
        data = pd.DataFrame(holdings, columns=PORTFOLIO_COLUMNS)
        return normalize_portfolio(data), None
    except Exception:
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS), "Portfolio load failed. The saved file may be damaged."


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
