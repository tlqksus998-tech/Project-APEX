from __future__ import annotations

import pandas as pd

from modules.market.master_search import search_as_dataframe, search_master


def search_tickers(query: str, limit: int = 30) -> pd.DataFrame:
    """Search tradable tickers from the canonical market database."""

    return search_master(query, limit)


def autocomplete_tickers(query: str, limit: int = 30) -> list[dict[str, str]]:
    """Return search results as simple dictionaries for UI autocomplete."""

    frame = search_as_dataframe(query, limit)
    if frame.empty:
        return []
    return [
        {
            "ticker": str(row.ticker),
            "name": str(row.name),
            "market": str(row.market),
            "asset_type": str(row.asset_type),
            "label": str(row.label),
        }
        for row in frame.itertuples(index=False)
    ]
