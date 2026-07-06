from __future__ import annotations

import pandas as pd

from modules.market.ticker_utils import infer_market

EMPTY_METRICS = {
    "total_invested": 0.0,
    "total_current_value": 0.0,
    "profit_loss": 0.0,
    "return_rate": 0.0,
    "krw_current_value": 0.0,
    "usd_current_value_original": 0.0,
    "krw_weight": 0.0,
    "usd_weight": 0.0,
}

US_MARKETS = {"US", "NASDAQ", "NYSE", "AMEX", "NYSEARCA", "OTHER"}


def calculate_portfolio_summary(portfolio: pd.DataFrame, prices: pd.DataFrame, usdkrw: float = 1380.0) -> tuple[pd.DataFrame, dict[str, float]]:
    """Calculate portfolio valuation with KRW/USD currency normalization."""

    if portfolio.empty:
        return pd.DataFrame(), EMPTY_METRICS.copy()

    price_frame = prices.copy()
    for column in ["ticker", "current_price", "price_source", "market", "currency"]:
        if column not in price_frame.columns:
            price_frame[column] = None

    merged = portfolio.merge(price_frame[["ticker", "current_price", "price_source", "market", "currency"]], on="ticker", how="left")
    merged["quantity"] = pd.to_numeric(merged["quantity"], errors="coerce").fillna(0.0)
    merged["avg_price"] = pd.to_numeric(merged["avg_price"], errors="coerce").fillna(0.0)
    merged["current_price"] = pd.to_numeric(merged["current_price"], errors="coerce").fillna(0.0)
    merged["price_source"] = merged["price_source"].fillna("missing")
    merged["market"] = merged.apply(lambda row: infer_position_market(row.get("ticker"), row.get("market")), axis=1)
    merged["trading_currency"] = merged.apply(lambda row: infer_trading_currency(row.get("ticker"), row.get("market"), row.get("currency")), axis=1)
    merged["fx_rate"] = merged["trading_currency"].map(lambda currency: safe_usdkrw(usdkrw) if currency == "USD" else 1.0)

    merged["average_price_original"] = merged["avg_price"]
    merged["current_price_original"] = merged["current_price"]
    merged["invested_amount_original"] = merged["quantity"] * merged["average_price_original"]
    merged["value_original_currency"] = merged["quantity"] * merged["current_price_original"]
    merged["value_krw"] = merged["value_original_currency"] * merged["fx_rate"]
    merged["invested_amount_krw"] = merged["invested_amount_original"] * merged["fx_rate"]

    # Backward-compatible columns now use KRW-normalized totals for portfolio-level logic.
    merged["invested_amount"] = merged["invested_amount_krw"]
    merged["current_value"] = merged["value_krw"]
    merged["profit_loss"] = merged["current_value"] - merged["invested_amount"]
    merged["profit_loss_original"] = merged["value_original_currency"] - merged["invested_amount_original"]
    merged["return_rate"] = merged.apply(
        lambda row: row["profit_loss_original"] / row["invested_amount_original"] if row["invested_amount_original"] > 0 else 0.0,
        axis=1,
    )

    total_invested = float(merged["invested_amount"].sum())
    total_current_value = float(merged["current_value"].sum())
    profit_loss = total_current_value - total_invested
    return_rate = profit_loss / total_invested if total_invested > 0 else 0.0

    if total_current_value > 0:
        merged["weight"] = merged["current_value"] / total_current_value
    else:
        merged["weight"] = 0.0

    krw_current_value = float(merged.loc[merged["trading_currency"] == "KRW", "value_krw"].sum())
    usd_current_value_original = float(merged.loc[merged["trading_currency"] == "USD", "value_original_currency"].sum())
    usd_current_value_krw = float(merged.loc[merged["trading_currency"] == "USD", "value_krw"].sum())

    metrics = {
        "total_invested": total_invested,
        "total_current_value": total_current_value,
        "profit_loss": profit_loss,
        "return_rate": return_rate,
        "krw_current_value": krw_current_value,
        "usd_current_value_original": usd_current_value_original,
        "usd_current_value_krw": usd_current_value_krw,
        "krw_weight": krw_current_value / total_current_value if total_current_value > 0 else 0.0,
        "usd_weight": usd_current_value_krw / total_current_value if total_current_value > 0 else 0.0,
    }
    return merged, metrics


def infer_position_market(ticker: object, market: object) -> str:
    """Infer a stable market label for a portfolio row."""

    value = str(market or "").strip().upper()
    if value and value != "NONE":
        return value
    inferred = infer_market(str(ticker or ""))
    return "US" if inferred == "US" else "KR" if inferred == "KR" else "UNKNOWN"


def infer_trading_currency(ticker: object, market: object, currency: object = None) -> str:
    """Infer trading currency without treating KRX alphanumeric codes as US tickers."""

    explicit = str(currency or "").strip().upper()
    if explicit in {"KRW", "USD"}:
        return explicit
    market_value = str(market or "").strip().upper()
    if market_value in {"KR", "KRX", "KOSPI", "KOSDAQ", "KONEX"}:
        return "KRW"
    if market_value in US_MARKETS:
        return "USD"
    inferred = infer_market(str(ticker or ""))
    return "USD" if inferred == "US" else "KRW"


def safe_usdkrw(value: float) -> float:
    """Return a positive USD/KRW rate with the app default fallback."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 1380.0
    return numeric if numeric > 0 else 1380.0


def calculate_portfolio_metrics(portfolio: pd.DataFrame, prices: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Backward-compatible alias for the Sprint 1 calculator."""

    return calculate_portfolio_summary(portfolio, prices)
