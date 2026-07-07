from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ThemeNewsItem:
    """One theme-related news item."""

    title: str
    source: str
    published_at: datetime
    url: str
    summary: str
    theme: str
    related_tickers: list[str]
    impact_level: str
    sentiment_label: str
    is_fallback: bool


@dataclass(frozen=True)
class ThemeNewsResult:
    """Theme news fetch result."""

    theme: str
    items: list[ThemeNewsItem]
    updated_at: datetime
    source: str
    success: bool
    is_fallback: bool
    error_message: str = ""
