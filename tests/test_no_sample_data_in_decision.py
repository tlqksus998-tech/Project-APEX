from __future__ import annotations

import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from modules.market.market_models import OHLCVDataResult, PriceData
from modules.ranking import ai_ranking_service as service


def test_sample_data_does_not_enter_decision_engine(monkeypatch) -> None:
    """Sample or fallback data should stop before decide_one is called."""

    fixed_now = datetime(2026, 7, 8, 10, 0, tzinfo=ZoneInfo("Asia/Seoul"))
    data = pd.DataFrame({"date": [pd.Timestamp(fixed_now)], "open": [1], "high": [1], "low": [1], "close": [1], "volume": [1]})
    called = {"decision": False}

    monkeypatch.setattr(service, "now_datetime", lambda: fixed_now)
    monkeypatch.setattr(service, "get_current_price", lambda ticker, config, market_hint=None: PriceData(ticker, ticker, market_hint or "KOSPI", 1.0, "KRW", "fallback", False, "fallback"))
    monkeypatch.setattr(service, "get_ohlcv", lambda request, config: OHLCVDataResult(request.ticker, request.ticker, request.market_hint or "KOSPI", data, "sample", False, "sample"))

    def fake_decide(_analysis):
        called["decision"] = True
        raise AssertionError("Decision engine should not be called")

    monkeypatch.setattr(service, "decide_one", fake_decide)
    service.clear_ai_judgement_cache()

    result = service.get_unified_ai_judgement("테스트", "TEST", "KOSPI")

    assert called["decision"] is False
    assert result.is_decision_allowed is False
    assert result.ai_score is None
    assert result.final_signal == "DATA_UNAVAILABLE"
