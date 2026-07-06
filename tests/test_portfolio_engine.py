import pandas as pd

from modules.portfolio_engine import CashPosition, calculate_total_cash, run_portfolio_engine
from modules.portfolio_engine.asset_models import Asset
from modules.portfolio_engine.calculator import build_assets_from_positions


def test_asset_model_creation():
    asset = Asset(ticker="AAPL", name="Apple", asset_type="Stock", market="NASDAQ", trading_currency="USD", exposure_region="US")

    assert asset.ticker == "AAPL"
    assert asset.trading_currency == "USD"


def test_krw_usd_cash_calculation():
    cash = CashPosition(krw_cash=100000, usd_cash=100, usdkrw=1380)

    assert cash.total_cash_krw == 238000
    assert calculate_total_cash(100000, 100, 1380) == 238000


def test_usd_asset_krw_conversion():
    positions = pd.DataFrame([{"ticker": "AAPL", "name": "Apple", "market": "NASDAQ", "quantity": 2, "avg_price": 100, "current_price": 150}])
    assets = build_assets_from_positions(positions, CashPosition(usdkrw=1380))

    assert assets[0].value_original_currency == 300
    assert assets[0].value_krw == 414000


def test_portfolio_engine_total_assets():
    positions = pd.DataFrame([{"ticker": "005930", "name": "Samsung", "market": "KOSPI", "quantity": 10, "avg_price": 70000, "current_price": 80000}])
    metrics = {"total_invested": 700000, "total_current_value": 800000}
    snapshot = run_portfolio_engine(positions, metrics, CashPosition(krw_cash=200000, usd_cash=100, usdkrw=1380))

    assert snapshot.total_assets_krw == 1_138_000
    assert snapshot.total_cash_krw == 338000
    assert snapshot.cash_ratio > 0


def test_currency_normalization_by_ticker_and_market():
    from modules.portfolio.calculator import calculate_portfolio_summary, infer_trading_currency

    assert infer_trading_currency("MU", "US") == "USD"
    assert infer_trading_currency("KORU", "NYSEARCA") == "USD"
    assert infer_trading_currency("000660", "KR") == "KRW"
    assert infer_trading_currency("360750", "KR") == "KRW"
    assert infer_trading_currency("0126Z0", "KR") == "KRW"

    portfolio = pd.DataFrame(
        [
            {"name": "SK hynix", "ticker": "000660", "quantity": 2, "avg_price": 100000},
            {"name": "Micron", "ticker": "MU", "quantity": 3, "avg_price": 100},
        ]
    )
    prices = pd.DataFrame(
        [
            {"ticker": "000660", "current_price": 120000, "price_source": "test", "market": "KR", "currency": "KRW"},
            {"ticker": "MU", "current_price": 110, "price_source": "test", "market": "US", "currency": "USD"},
        ]
    )
    positions, metrics = calculate_portfolio_summary(portfolio, prices, usdkrw=1380)

    assert positions.loc[positions["ticker"] == "MU", "value_krw"].iloc[0] == 3 * 110 * 1380
    assert positions.loc[positions["ticker"] == "000660", "value_krw"].iloc[0] == 2 * 120000
    assert metrics["total_current_value"] == (2 * 120000) + (3 * 110 * 1380)
    assert metrics["usd_current_value_original"] == 330
