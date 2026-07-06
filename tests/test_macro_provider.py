from __future__ import annotations

import pandas as pd

from modules.market import macro_provider
from modules.market.macro_provider import build_macro_brief, build_fallback_history, calculate_macro_score, fetch_macro_instrument


def test_macro_provider_falls_back_when_history_fails(monkeypatch):
    def fail_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
        raise RuntimeError("network down")

    monkeypatch.setattr(macro_provider, "cached_yfinance_history", fail_history)

    result, history = fetch_macro_instrument("KOSPI", "^KS11", "1mo", "1d")

    assert result.success is False
    assert result.source == "fallback"
    assert not history.empty
    assert {"date", "close"}.issubset(history.columns)


def test_macro_brief_result_shape_with_sample_data(monkeypatch):
    def sample_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
        history = build_fallback_history("KOSPI", periods=5).copy()
        return history.rename(columns={"date": "Date", "close": "Close"})

    monkeypatch.setattr(macro_provider, "cached_yfinance_history", sample_history)

    brief = build_macro_brief(period="1mo", interval="1d")

    assert 0 <= brief.macro_score <= 100
    assert brief.traffic_light in {"🟢 우호적", "🟡 관망", "🔴 리스크 확대"}
    assert len(brief.overview) == 8
    assert "KOSPI" in brief.histories


def test_macro_score_range_for_empty_input():
    assert calculate_macro_score(pd.DataFrame()) == 50.0
