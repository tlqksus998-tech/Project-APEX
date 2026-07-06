from __future__ import annotations

import pandas as pd

from modules.market.ticker_utils import infer_market, is_us_stock_ticker
from modules.portfolio_engine.asset_models import Asset
from modules.portfolio_engine.cash_manager import CashPosition, calculate_investable_cash
from modules.portfolio_engine.models import PortfolioEngineSnapshot

US_MARKETS = {"US", "NASDAQ", "NYSE", "AMEX", "NYSEARCA", "OTHER"}
KR_MARKETS = {"KR", "KRX", "KOSPI", "KOSDAQ", "KONEX"}


def infer_currency(market: str, ticker: str = "") -> str:
    """Infer trading currency from market/ticker without misclassifying KRX special codes."""

    value = str(market or "").upper()
    if value in KR_MARKETS:
        return "KRW"
    if value in US_MARKETS:
        return "USD"
    inferred = infer_market(str(ticker or ""))
    if inferred == "KR":
        return "KRW"
    if inferred == "US" or is_us_stock_ticker(str(ticker or "")):
        return "USD"
    return "KRW"


def infer_region(market: str, ticker: str = "") -> str:
    """Infer exposure region from market/ticker."""

    value = str(market or "").upper()
    if value in KR_MARKETS:
        return "Korea"
    if value in US_MARKETS:
        return "US"
    inferred = infer_market(str(ticker or ""))
    return "US" if inferred == "US" else "Korea" if inferred == "KR" else "Unknown"


def build_assets_from_positions(positions: pd.DataFrame, cash: CashPosition | None = None) -> list[Asset]:
    """Convert existing portfolio positions into Asset models."""

    if positions is None or positions.empty:
        return []
    cash = cash or CashPosition()
    assets: list[Asset] = []
    for row in positions.to_dict(orient="records"):
        ticker = str(row.get("ticker", ""))
        market = str(row.get("market", "KR") or "KR")
        currency = str(row.get("trading_currency") or infer_currency(market, ticker)).upper()
        fx_rate = cash.usdkrw if currency == "USD" else 1.0
        quantity = safe_float(row.get("quantity"))
        average_price = safe_float(row.get("average_price_original", row.get("avg_price")))
        current_price = safe_float(row.get("current_price_original", row.get("current_price")))
        original_value = safe_float(row.get("value_original_currency", quantity * current_price))
        value_krw = safe_float(row.get("value_krw", original_value * fx_rate))
        assets.append(
            Asset(
                ticker=ticker,
                name=str(row.get("name", ticker)),
                asset_type=str(row.get("asset_type", "Stock") or "Stock"),
                market=market,
                trading_currency=currency,
                exposure_region=infer_region(market, ticker),
                quantity=quantity,
                average_price=average_price,
                current_price=current_price,
                average_price_original=average_price,
                current_price_original=current_price,
                value_original_currency=original_value,
                fx_rate=fx_rate,
                value_krw=value_krw,
                weight=safe_float(row.get("weight")),
            )
        )
    return normalize_asset_weights(assets)


def normalize_asset_weights(assets: list[Asset]) -> list[Asset]:
    """Normalize asset weights by KRW value."""

    total = sum(asset.value_krw for asset in assets)
    if total <= 0:
        return assets
    return [asset.__class__(**{**asset.__dict__, "weight": asset.value_krw / total}) for asset in assets]


def build_portfolio_snapshot(positions: pd.DataFrame, metrics: dict[str, float] | None, cash: CashPosition | None = None) -> PortfolioEngineSnapshot:
    """Build an operating-system portfolio snapshot from existing app outputs."""

    cash = cash or CashPosition()
    metrics = metrics or {}
    assets = build_assets_from_positions(positions, cash)
    invested = float(metrics.get("total_invested", 0.0) or 0.0)
    asset_value = sum(asset.value_krw for asset in assets) or float(metrics.get("total_current_value", 0.0) or 0.0)
    total_cash = cash.total_cash_krw
    total_assets = asset_value + total_cash
    cash_ratio = total_cash / total_assets if total_assets > 0 else 0.0
    krw_asset_value = sum(asset.value_krw for asset in assets if asset.trading_currency == "KRW")
    usd_asset_value_krw = sum(asset.value_krw for asset in assets if asset.trading_currency == "USD")
    usd_asset_value_original = sum(asset.value_original_currency for asset in assets if asset.trading_currency == "USD")
    return PortfolioEngineSnapshot(
        assets=assets,
        total_assets_krw=total_assets,
        total_invested_krw=invested,
        total_cash_krw=total_cash,
        total_current_value_krw=asset_value,
        krw_current_value=krw_asset_value,
        usd_current_value_original=usd_asset_value_original,
        usd_current_value_krw=usd_asset_value_krw,
        cash_ratio=cash_ratio,
        krw_cash=max(cash.krw_cash, 0.0),
        usd_cash=max(cash.usd_cash, 0.0),
        usdkrw=max(cash.usdkrw, 0.0),
        krw_weight=currency_weight(assets, "KRW", total_assets, total_cash, cash.krw_cash),
        usd_weight=currency_weight(assets, "USD", total_assets, total_cash, cash.usd_cash * cash.usdkrw),
        korea_exposure=region_weight(assets, "Korea", total_assets),
        us_exposure=region_weight(assets, "US", total_assets),
        investable_cash_krw=calculate_investable_cash(total_cash),
        market_weights=group_weight(assets, "market", total_assets),
        currency_weights=group_weight(assets, "trading_currency", total_assets),
    )


def group_weight(assets: list[Asset], attr: str, total_assets: float) -> dict[str, float]:
    """Group asset KRW weights by an Asset attribute."""

    if total_assets <= 0:
        return {}
    result: dict[str, float] = {}
    for asset in assets:
        key = str(getattr(asset, attr))
        result[key] = result.get(key, 0.0) + asset.value_krw / total_assets
    return result


def currency_weight(assets: list[Asset], currency: str, total_assets: float, total_cash: float, cash_value: float) -> float:
    """Calculate currency weight including cash."""

    if total_assets <= 0:
        return 0.0
    asset_value = sum(asset.value_krw for asset in assets if asset.trading_currency == currency)
    return (asset_value + max(cash_value, 0.0)) / total_assets


def region_weight(assets: list[Asset], region: str, total_assets: float) -> float:
    """Calculate region exposure by KRW asset value."""

    if total_assets <= 0:
        return 0.0
    return sum(asset.value_krw for asset in assets if asset.exposure_region == region) / total_assets


def safe_float(value: object) -> float:
    """Convert a value to float with zero fallback."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if pd.isna(numeric):
        return 0.0
    return numeric
