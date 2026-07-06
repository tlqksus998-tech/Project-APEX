from __future__ import annotations

from datetime import datetime

from modules.market import fx_provider
from modules.market.fx_provider import FxRateResult, get_usdkrw_rate


def test_fx_provider_returns_fallback_when_yfinance_unavailable(monkeypatch):
    monkeypatch.setattr(fx_provider, "yf", None)

    result = get_usdkrw_rate(1399.0)

    assert isinstance(result, FxRateResult)
    assert result.pair == "USD/KRW"
    assert result.rate == 1399.0
    assert result.success is False
    assert result.source == "fallback"


def test_fx_rate_result_shape():
    result = FxRateResult("USD/KRW", 1380.0, "test", True, datetime.now(), "OK")

    assert result.rate == 1380.0
    assert result.success is True
    assert result.message == "OK"
