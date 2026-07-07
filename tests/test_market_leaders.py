from __future__ import annotations

from modules.market.market_leaders import MarketLeaderItem, get_kospi_market_cap_top10, get_market_leaders, get_nasdaq_market_cap_top10
from app.ui.market_leaders_view import LEADER_SECTIONS


def test_market_leader_item_creation():
    item = MarketLeaderItem(1, "005930", "삼성전자", "KOSPI", 80000, 0.1, 1_000_000, 100_000, "KRW", "now", "test")
    assert item.rank == 1
    assert item.ticker == "005930"


def test_kospi_top10_failure_does_not_break_app():
    items, _ = get_kospi_market_cap_top10()
    assert isinstance(items, list)
    assert len(items) <= 10


def test_nasdaq_top10_returns_mvp_universe():
    items, _ = get_nasdaq_market_cap_top10()
    assert isinstance(items, list)
    assert len(items) == 10
    assert items[0].market == "NASDAQ"


def test_get_market_leaders_returns_result_object():
    result = get_market_leaders()
    assert hasattr(result, "kospi_market_cap_top10")
    assert hasattr(result, "nasdaq_trading_value_top10")
    assert isinstance(result.error_message, str)


def test_market_leader_section_ids_are_unique():
    section_ids = [section_id for section_id, _ in LEADER_SECTIONS]
    assert section_ids == ["kospi_market_cap", "kospi_trading_value", "nasdaq_market_cap", "nasdaq_trading_value"]
    assert len(section_ids) == len(set(section_ids))
