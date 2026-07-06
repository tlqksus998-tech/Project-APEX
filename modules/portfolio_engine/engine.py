from __future__ import annotations

import pandas as pd

from modules.portfolio_engine.calculator import build_assets_from_positions, build_portfolio_snapshot
from modules.portfolio_engine.cash_manager import CashPosition
from modules.portfolio_engine.models import PortfolioEngineSnapshot


def run_portfolio_engine(positions: pd.DataFrame, metrics: dict[str, float] | None, cash: CashPosition | None = None) -> PortfolioEngineSnapshot:
    """Run the portfolio operating engine foundation."""

    return build_portfolio_snapshot(positions, metrics, cash or CashPosition())


__all__ = ["build_assets_from_positions", "run_portfolio_engine"]
