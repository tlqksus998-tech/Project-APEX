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


SAMSUNG_ELECTRO = "\uc0bc\uc131\uc804\uae30"
SK_SQUARE = "SK\uc2a4\ud018\uc5b4"


def test_kospi_required_names_are_searchable():
    samsung_electro = search_as_dataframe(SAMSUNG_ELECTRO, limit=10)
    sk_square = search_as_dataframe(SK_SQUARE, limit=10)
    samsung = search_as_dataframe("\uc0bc\uc131", limit=30)

    assert "009150" in samsung_electro["ticker"].tolist()
    assert "402340" in sk_square["ticker"].tolist()
    assert "005930" in samsung["ticker"].tolist()
    assert "009150" in samsung["ticker"].tolist()


def test_kospi_ticker_search_and_cache_columns():
    from modules.market.master_cache import read_master_cache
    from modules.market.master_loader import refresh_krx_master_cache
    from modules.market.master_search import search_master

    refreshed = refresh_krx_master_cache()
    cached = read_master_cache("krx_master")
    ticker_result = search_master("009150", limit=5)

    assert not refreshed.empty
    assert {"name", "ticker", "market", "asset_type", "search_text"}.issubset(cached.columns)
    assert "009150" in ticker_result["ticker"].tolist()
