from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


@dataclass(frozen=True)
class SentimentIndicator:
    """Placeholder sentiment indicator for future external API integration."""

    name: str
    value: str
    label: str
    updated_at: datetime
    source: str
    is_placeholder: bool


def get_fear_greed_placeholder() -> SentimentIndicator:
    """Return a clearly marked placeholder Fear & Greed indicator."""

    return SentimentIndicator(
        name="Fear & Greed",
        value="준비 중",
        label="향후 연동 예정",
        updated_at=datetime.now(KST),
        source="demo_placeholder",
        is_placeholder=True,
    )
