from __future__ import annotations

from modules.market.sentiment_provider import SentimentIndicator, get_fear_greed_placeholder


def test_sentiment_placeholder_returns_demo_indicator():
    sentiment = get_fear_greed_placeholder()

    assert isinstance(sentiment, SentimentIndicator)
    assert sentiment.name == "Fear & Greed"
    assert sentiment.value == "준비 중"
    assert sentiment.is_placeholder is True
    assert sentiment.source == "demo_placeholder"
