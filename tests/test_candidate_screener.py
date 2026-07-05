import pandas as pd

from modules.screening.candidate_screener import screen_today_candidates


def test_candidate_screener_returns_dataframe_from_master():
    master = pd.DataFrame(
        [
            {"name": "A", "ticker": "000001", "market": "KOSPI", "asset_type": "Stock"},
            {"name": "B", "ticker": "000002", "market": "KOSPI", "asset_type": "Stock"},
        ]
    )

    result = screen_today_candidates(master=master, limit=2)

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["name", "ticker", "market", "final_score", "decision", "reasons"]


def test_candidate_screener_sorts_by_final_score_from_analysis():
    analysis = pd.DataFrame(
        [
            {"ticker": "AAA", "name": "A", "market": "KOSPI", "trend_status": "\uc0c1\uc2b9\ucd94\uc138", "rsi_14": 45, "macd_status": "\uc0c1\uc2b9 \ubaa8\uba58\ud140", "volume_status": "\uac70\ub798\ub7c9 \ubcf4\ud1b5", "week52_position": 50},
            {"ticker": "BBB", "name": "B", "market": "KOSPI", "trend_status": "\uc0c1\uc2b9\ucd94\uc138", "rsi_14": 50, "macd_status": "\uc0c1\uc2b9 \ubaa8\uba58\ud140", "volume_status": "\uac70\ub798\ub7c9 \uc99d\uac00", "week52_position": 55},
        ]
    )
    decisions = pd.DataFrame(
        [
            {"ticker": "AAA", "final_score": 60, "decision": "HOLD", "reasons": ["a"]},
            {"ticker": "BBB", "final_score": 80, "decision": "BUY", "reasons": ["b"]},
        ]
    )

    result = screen_today_candidates(analysis, decisions, limit=2)

    assert result.iloc[0]["ticker"] == "BBB"
    assert result["final_score"].tolist() == sorted(result["final_score"].tolist(), reverse=True)


def test_candidate_screener_handles_empty_data():
    result = screen_today_candidates(master=pd.DataFrame(), limit=5)

    assert isinstance(result, pd.DataFrame)
    assert result.empty
