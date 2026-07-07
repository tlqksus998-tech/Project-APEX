from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.analysis import analyze_many
from modules.config import get_config
from modules.decision import decide_many
from modules.market import build_market_overview
from modules.portfolio.calculator import calculate_portfolio_summary
from modules.portfolio_engine import CashPosition
from modules.risk import evaluate_portfolio_risk

K_ENGINE_ERROR = "가격 또는 분석 데이터를 가져오지 못했습니다. 티커를 확인하거나 잠시 후 다시 시도하세요."


def prices_from_market_overview(overview: pd.DataFrame) -> pd.DataFrame:
    """Convert market overview rows into portfolio price rows."""

    if overview.empty:
        return pd.DataFrame(columns=["ticker", "current_price", "price_source", "market", "currency"])
    return overview[["ticker", "current_price", "source", "market", "currency"]].rename(columns={"source": "price_source"})


def run_dashboard_engines(
    portfolio: pd.DataFrame,
    cash: CashPosition,
    period: str,
    interval: str,
    market_regime: str = "NEUTRAL",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float], pd.DataFrame]:
    """Run market, analysis, decision, and risk engines with a friendly fallback."""

    try:
        config = get_config()
        tickers = portfolio["ticker"].tolist() if not portfolio.empty else []
        market_overview, histories = build_market_overview(tickers, config, period=period, interval=interval)
        analysis_results = analyze_many(histories)
        positions, metrics = calculate_portfolio_summary(portfolio, prices_from_market_overview(market_overview), usdkrw=cash.usdkrw)
        portfolio_risk = evaluate_portfolio_risk(positions, cash_amount=cash.total_cash_krw)
        decision_results = decide_many(analysis_results, portfolio_risk, market_regime=market_regime)
        return market_overview, analysis_results, positions, portfolio_risk, metrics, decision_results
    except Exception:
        st.warning(K_ENGINE_ERROR)
        empty_metrics = {"total_invested": 0.0, "total_current_value": 0.0, "profit_loss": 0.0, "return_rate": 0.0}
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), empty_metrics, pd.DataFrame()
