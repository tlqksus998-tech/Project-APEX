from __future__ import annotations

import pandas as pd

from modules.config import AppConfig


def evaluate_risk_rules(position_df: pd.DataFrame, config: AppConfig) -> list[dict[str, str]]:
    """Evaluate simple Sprint 1 risk rules."""

    if position_df.empty:
        return [{"level": "warning", "title": "Empty Portfolio", "message": "No valid holdings are available for risk checks."}]

    alerts: list[dict[str, str]] = []
    max_weight = float(position_df["weight"].max()) if "weight" in position_df.columns else 0.0
    top_name = "N/A"
    if max_weight > 0 and "name" in position_df.columns:
        top_name = str(position_df.loc[position_df["weight"].idxmax(), "name"])

    if max_weight > config.concentration_limit:
        alerts.append(
            {
                "level": "danger",
                "title": "Position Concentration",
                "message": f"{top_name} is {max_weight:.1%} of the portfolio. Review single-position exposure.",
            }
        )
    else:
        alerts.append(
            {
                "level": "info",
                "title": "Concentration Check",
                "message": f"The largest position weight is {max_weight:.1%}.",
            }
        )

    current_value = float(position_df["current_value"].sum()) if "current_value" in position_df.columns else 0.0
    cash_weight = 0.0 if current_value > 0 else 1.0
    if cash_weight < config.cash_minimum_weight:
        alerts.append(
            {
                "level": "warning",
                "title": "Low Cash Buffer",
                "message": "Sprint 1 does not track cash, so the cash buffer is treated as low.",
            }
        )

    if len(position_df) < 3:
        alerts.append(
            {
                "level": "warning",
                "title": "Limited Diversification",
                "message": "Fewer than three valid holdings were entered.",
            }
        )

    return alerts
