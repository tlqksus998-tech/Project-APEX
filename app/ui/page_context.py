from __future__ import annotations

from dataclasses import dataclass

from modules.data_freshness import DataFreshnessSnapshot
from modules.market.macro_models import MacroBriefResult
from modules.market.sentiment_provider import SentimentIndicator
from modules.portfolio_engine import CashPosition


@dataclass(frozen=True)
class PageContext:
    """Runtime values shared by page renderers."""

    selected_menu: str
    user_mode: str
    beginner_mode: bool
    period: str
    interval: str
    cash: CashPosition
    macro_brief: MacroBriefResult
    sentiment: SentimentIndicator
    freshness: DataFreshnessSnapshot
