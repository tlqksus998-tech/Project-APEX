from __future__ import annotations

import pandas as pd


EMPTY_METRICS = {
    "total_invested": 0.0,
    "total_current_value": 0.0,
    "profit_loss": 0.0,
    "return_rate": 0.0,
}


def calculate_portfolio_summary(portfolio: pd.DataFrame, prices: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Calculate Sprint 1 portfolio valuation summary."""

    if portfolio.empty:
        return pd.DataFrame(), EMPTY_METRICS.copy()

    price_frame = prices.copy()
    for column in ["ticker", "current_price", "price_source"]:
        if column not in price_frame.columns:
            price_frame[column] = None

    merged = portfolio.merge(price_frame[["ticker", "current_price", "price_source"]], on="ticker", how="left")
    merged["current_price"] = pd.to_numeric(merged["current_price"], errors="coerce").fillna(0.0)
    merged["price_source"] = merged["price_source"].fillna("missing")
    merged["invested_amount"] = merged["quantity"] * merged["avg_price"]
    merged["current_value"] = merged["quantity"] * merged["current_price"]
    merged["profit_loss"] = merged["current_value"] - merged["invested_amount"]
    merged["return_rate"] = merged.apply(
        lambda row: row["profit_loss"] / row["invested_amount"] if row["invested_amount"] > 0 else 0.0,
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

    metrics = {
        "total_invested": total_invested,
        "total_current_value": total_current_value,
        "profit_loss": profit_loss,
        "return_rate": return_rate,
    }
    return merged, metrics


def calculate_portfolio_metrics(portfolio: pd.DataFrame, prices: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Backward-compatible alias for the Sprint 1 calculator."""

    return calculate_portfolio_summary(portfolio, prices)
