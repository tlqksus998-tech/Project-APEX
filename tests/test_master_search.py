from modules.market.master_cache import MARKET_DATA_DIR, cache_exists
from modules.market.master_loader import load_master_database
from modules.market.master_search import measure_search_latency, search_as_dataframe

QUERIES = [
    "\uc0bc\uc131",
    "SK\ud558\uc774\ub2c9\uc2a4",
    "\ud604\ub300",
    "LG",
    "POSCO",
    "NAVER",
    "\uce74\uce74\uc624",
    "TIGER",
    "KODEX",
    "ACE",
    "SOXL",
    "QQQ",
    "SPY",
    "NVDA",
    "AAPL",
    "MSFT",
    "MU",
    "KORU",
]


def test_master_database_loads_and_creates_cache():
    data = load_master_database()

    assert not data.empty
    assert {"ticker", "name", "english_name", "market", "asset_type", "source"}.issubset(data.columns)
    assert MARKET_DATA_DIR.exists()
    assert cache_exists()


def test_master_search_requested_queries_return_results():
    for query in QUERIES:
        result = search_as_dataframe(query, limit=30)
        assert not result.empty, query


def test_exact_name_or_ticker_ranked_near_top():
    samsung = search_as_dataframe("\uc0bc\uc131\uc804\uc790", limit=5)
    soxl = search_as_dataframe("SOXL", limit=5)
    nvidia = search_as_dataframe("NVIDIA", limit=5)

    assert samsung.iloc[0]["ticker"] == "005930"
    assert soxl.iloc[0]["ticker"] == "SOXL"
    assert "NVDA" in nvidia["ticker"].tolist()


def test_search_latency_after_warmup_under_target():
    search_as_dataframe("\uc0bc\uc131", limit=30)
    elapsed = measure_search_latency("\uc0bc\uc131")

    assert elapsed < 0.2
