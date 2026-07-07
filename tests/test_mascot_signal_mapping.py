from __future__ import annotations

from app.ui.mascot import get_mascot_for_signal


def test_buy_signals_map_to_cabbage() -> None:
    """Positive or maintain signals should use 배추거북이."""

    for signal in ["BUY_APPROVED", "STRONG_BUY", "BUY", "HOLD"]:
        assert get_mascot_for_signal(signal)["role"] == "cabbage"


def test_watch_signals_map_to_mushroom() -> None:
    """Watchlist-style signals should use 버섯거북이."""

    for signal in ["WATCH", "INTEREST", "REENTRY_CANDIDATE"]:
        assert get_mascot_for_signal(signal)["role"] == "mushroom"


def test_wait_signals_map_to_tofu_pouch() -> None:
    """Neutral, unknown, and missing signals should use 유부거북이."""

    for signal in ["WAIT", "NEUTRAL", "UNKNOWN", "unknown", None]:
        assert get_mascot_for_signal(signal)["role"] == "tofu_pouch"


def test_reduce_signals_map_to_meat() -> None:
    """Risky sell-side signals should use 고기거북이."""

    for signal in ["REDUCE", "SELL", "DO_NOT_BUY", "DO NOT BUY", "do-not-buy"]:
        assert get_mascot_for_signal(signal)["role"] == "meat"
