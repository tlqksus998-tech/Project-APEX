from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.help_text import help_for
from modules.decision.decision_engine import map_decision
from modules.utils import format_currency, format_percent


K_TITLE = "\U0001f4c8 \uc624\ub298\uc758 \ud22c\uc790\ud310\ub2e8"
K_ACTION_TITLE = "\uc624\ub298 \ud574\uc57c \ud560 \ud589\ub3d9"
K_TABLE_TITLE = "\ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ud14c\uc774\ube14"
K_NO_TABLE = "\uc544\uc9c1 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \uc885\ubaa9\uc744 \uac80\uc0c9\ud574 \ucd94\uac00\ud574\ubcf4\uc138\uc694."
K_NAME = "\uc885\ubaa9\uba85"
K_TICKER = "\ud2f0\ucee4"
K_PRICE = "\ud604\uc7ac\uac00"
K_RETURN = "\uc218\uc775\ub960"
K_INVESTED = "\ucd1d \ud22c\uc790\uae08\uc561"
K_VALUE = "\ud3c9\uac00\uae08\uc561"
K_PROFIT = "\ud3c9\uac00\uc190\uc775"
K_CASH = "\ud604\uae08\ube44\uc911"
K_CONCENTRATION = "\uc9d1\uc911\ub3c4"

DECISION_DESCRIPTIONS = {
    "STRONG_BUY": "\uae30\uc220\uc801 \ud750\ub984\uc740 \uc591\ud638\ud558\uc9c0\ub9cc \uacfc\ub3c4\ud55c \ube44\uc911\ud655\ub300\ubcf4\ub2e4 \ubd84\ud560\ub9e4\uc218 \uad00\uc810\uc73c\ub85c \uc811\uadfc\ud558\uc138\uc694.",
    "BUY": "\uae30\uc220\uc801 \ud750\ub984\uc740 \uc591\ud638\ud558\uc9c0\ub9cc \ubd84\ud560\ub9e4\uc218 \uad00\uc810\uc73c\ub85c \uc811\uadfc\ud558\uc138\uc694.",
    "HOLD": "\ud604\uc7ac\ub294 \ubcf4\uc720\ub97c \uc720\uc9c0\ud558\ub294 \uac83\uc774 \uc801\uc808\ud569\ub2c8\ub2e4. \ub2e4\ub9cc \ube44\uc911\uc774 \ub192\uac70\ub098 \ud604\uae08\uc774 \ubd80\uc871\ud558\uba74 \ucd94\uac00\ub9e4\uc218\ub294 \ubcf4\ub958\ud558\uc138\uc694.",
    "REDUCE": "\ube44\uc911 \ub610\ub294 \ub9ac\uc2a4\ud06c\uac00 \ub192\uc2b5\ub2c8\ub2e4. \uc77c\ubd80 \ube44\uc911 \ucd95\uc18c\ub97c \uac80\ud1a0\ud558\uc138\uc694.",
    "SELL": "\ud604\uc7ac \ub9ac\uc2a4\ud06c\uac00 \ub192\uc2b5\ub2c8\ub2e4. \uc190\uc2e4 \ud655\ub300 \ubc29\uc9c0\ub97c \uc6b0\uc120 \uac80\ud1a0\ud558\uc138\uc694.",
}

DECISION_COLORS = {
    "STRONG_BUY": "background-color: #dcfce7; color: #166534; font-weight: 700;",
    "BUY": "background-color: #dcfce7; color: #166534; font-weight: 700;",
    "HOLD": "background-color: #dbeafe; color: #1e40af; font-weight: 700;",
    "REDUCE": "background-color: #ffedd5; color: #9a3412; font-weight: 700;",
    "SELL": "background-color: #fee2e2; color: #991b1b; font-weight: 700;",
}


def render_today_title() -> None:
    """Render the main Today Dashboard title."""

    st.markdown(f"## {K_TITLE}")


def compute_dashboard_scores(decision_results: pd.DataFrame, portfolio_risk: pd.DataFrame) -> dict[str, float | str]:
    """Compute portfolio-level dashboard scores from existing engine outputs."""

    if decision_results.empty:
        return {"portfolio_score": 0.0, "market_score": 0.0, "risk_score": 0.0, "final_score": 0.0, "decision": "HOLD"}

    portfolio_score = float(pd.to_numeric(decision_results["final_score"], errors="coerce").fillna(0).mean())
    market_score = float(pd.to_numeric(decision_results["decision_score"], errors="coerce").fillna(0).mean())
    average_penalty = 0.0
    if not portfolio_risk.empty:
        average_penalty = float(pd.to_numeric(portfolio_risk["total_risk_penalty"], errors="coerce").fillna(0).mean())
    risk_score = max(0.0, min(100.0, 100.0 + average_penalty))
    final_score = max(0.0, min(100.0, (portfolio_score * 0.55) + (market_score * 0.25) + (risk_score * 0.20)))
    decision = map_decision(final_score).value
    return {"portfolio_score": portfolio_score, "market_score": market_score, "risk_score": risk_score, "final_score": final_score, "decision": decision}


def render_score_cards(scores: dict[str, float | str], beginner_mode: bool = True) -> None:
    """Render top score cards and the large decision card."""

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Portfolio Score", f"{float(scores['portfolio_score']):.1f}", help=help_for("Portfolio Score"))
    col2.metric("Market Score", f"{float(scores['market_score']):.1f}", help=help_for("Market Score"))
    col3.metric("Risk Score", f"{float(scores['risk_score']):.1f}", help=help_for("Risk Score"))
    col4.metric("Final Score", f"{float(scores['final_score']):.1f}", help=help_for("Final Score"))

    decision = str(scores["decision"])
    description = DECISION_DESCRIPTIONS.get(decision, DECISION_DESCRIPTIONS["HOLD"])
    st.markdown(
        f"""
        <div style="padding: 22px; border-radius: 12px; border: 1px solid #e5e7eb; text-align: center; margin: 10px 0 18px 0;">
            <div style="font-size: 14px; color: #6b7280;">Decision</div>
            <div style="font-size: 52px; font-weight: 800; letter-spacing: 0;">{decision}</div>
            <div style="font-size: 16px; color: #374151; margin-top: 8px;">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if beginner_mode:
        st.caption("Decision\uc740 \ub9e4\uc218/\ub9e4\ub3c4 \uc9c0\uc2dc\uac00 \uc544\ub2c8\ub77c \ud604\uc7ac \uc0c1\ud0dc\uc5d0\uc11c \uc5b4\ub5a4 \ud589\ub3d9\uc744 \uba3c\uc800 \uac80\ud1a0\ud560\uc9c0 \ub3d5\ub294 \ucd08\uc548\uc785\ub2c8\ub2e4.")


def build_today_actions(positions: pd.DataFrame, portfolio_risk: pd.DataFrame, scores: dict[str, float | str]) -> list[str]:
    """Build rule-based action items for today."""

    actions: list[str] = []
    decision = str(scores["decision"])
    if decision in {"REDUCE", "SELL"}:
        actions.append("\u2713 \uc2e0\uaddc\ub9e4\uc218 \ubcf4\ub958")
    elif decision == "HOLD":
        actions.append("\u2713 \uc2e0\uaddc\ub9e4\uc218\ub294 \ubd84\ud560 \uc811\uadfc\ub9cc \uac80\ud1a0")
    else:
        actions.append("\u2713 \ub9e4\uc218 \ud6c4\ubcf4\ub294 \ub9ac\uc2a4\ud06c \ud655\uc778 \ud6c4 \uc18c\uc561\uc73c\ub85c \uc81c\ud55c")

    if not positions.empty and float(positions["weight"].max()) >= 0.30:
        actions.append("\u2713 \ube44\uc911 30% \uc774\uc0c1 \uc885\ubaa9 \ud655\uc778")
    if not portfolio_risk.empty and portfolio_risk["leverage_risk"].ne("Normal").any():
        actions.append("\u2713 \ub808\ubc84\ub9ac\uc9c0 ETF \uc8fc\uc758")
    if float(scores["risk_score"]) < 90:
        actions.append("\u2713 \ud604\uae08\ube44\uc911 \ud655\ubcf4")
    if not portfolio_risk.empty and portfolio_risk["averaging_down_risk"].ne("Normal").any():
        actions.append("\u2713 \uc190\uc2e4 \uad6c\uac04 \ucd94\uac00\ub9e4\uc218 \uae08\uc9c0\uc120 \ud655\uc778")

    return actions[:5]


def render_action_card(actions: list[str]) -> None:
    """Render today's rule-based action card."""

    with st.container(border=True):
        st.subheader(K_ACTION_TITLE)
        for action in actions:
            st.write(action)


def build_dashboard_table(positions: pd.DataFrame, analysis_results: pd.DataFrame, decision_results: pd.DataFrame, portfolio_risk: pd.DataFrame) -> pd.DataFrame:
    """Build the merged portfolio dashboard table."""

    if positions.empty:
        return pd.DataFrame()

    table = positions[["name", "ticker", "current_price", "return_rate"]].copy()
    if not analysis_results.empty:
        table = table.merge(analysis_results[["ticker", "rsi_14", "macd", "trend_status", "week52_position"]], on="ticker", how="left")
    if not portfolio_risk.empty:
        risk = portfolio_risk[["ticker", "total_risk_penalty"]].copy()
        risk["risk"] = risk["total_risk_penalty"].map(lambda value: "High" if value <= -30 else "Medium" if value < 0 else "Low")
        table = table.merge(risk[["ticker", "risk"]], on="ticker", how="left")
    if not decision_results.empty:
        table = table.merge(decision_results[["ticker", "final_score", "decision"]], on="ticker", how="left")

    return table.rename(
        columns={
            "name": K_NAME,
            "ticker": K_TICKER,
            "current_price": K_PRICE,
            "return_rate": K_RETURN,
            "rsi_14": "RSI",
            "macd": "MACD",
            "trend_status": "Trend",
            "week52_position": "52W Position",
            "risk": "Risk",
            "final_score": "Final Score",
            "decision": "Decision",
        }
    )


def render_dashboard_table(table: pd.DataFrame, beginner_mode: bool = True) -> None:
    """Render the merged portfolio table with decision coloring."""

    st.subheader(K_TABLE_TITLE)
    if table.empty:
        st.info(K_NO_TABLE)
        return

    display = table.copy()
    if beginner_mode:
        keep_columns = [K_NAME, K_TICKER, K_PRICE, K_RETURN, "Trend", "Risk", "Final Score", "Decision"]
        display = display[[column for column in keep_columns if column in display.columns]]
    for column in [K_PRICE, "RSI", "MACD", "52W Position", "Final Score"]:
        if column in display.columns:
            numeric = pd.to_numeric(display[column], errors="coerce")
            display[column] = numeric.map(lambda value: None if pd.isna(value) else round(float(value), 2))
    if K_RETURN in display.columns:
        numeric_return = pd.to_numeric(display[K_RETURN], errors="coerce")
        display[K_RETURN] = numeric_return.map(lambda value: format_percent(float(value)) if pd.notna(value) else None)

    styled = display.style.map(color_decision_cell, subset=["Decision"])
    st.dataframe(styled, width="stretch", hide_index=True)


def color_decision_cell(value: object) -> str:
    """Return CSS for decision cells."""

    return DECISION_COLORS.get(str(value), "")


def render_portfolio_summary(positions: pd.DataFrame, metrics: dict[str, float], cash_amount: float) -> None:
    """Render portfolio summary metrics."""

    st.subheader("Portfolio Summary")
    total_value = float(metrics["total_current_value"])
    cash_ratio = cash_amount / (cash_amount + total_value) if (cash_amount + total_value) > 0 else 0.0
    concentration = float(positions["weight"].max()) if not positions.empty else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric(K_INVESTED, format_currency(metrics["total_invested"]))
    col2.metric(K_VALUE, format_currency(metrics["total_current_value"]))
    col3.metric(K_PROFIT, format_currency(metrics["profit_loss"]))

    col4, col5, col6 = st.columns(3)
    col4.metric(K_RETURN, format_percent(metrics["return_rate"]))
    col5.metric(K_CASH, format_percent(cash_ratio), help=help_for("Cash Ratio"))
    col6.metric(K_CONCENTRATION, format_percent(concentration), help=help_for("Concentration"))


def render_risk_alerts(portfolio_risk: pd.DataFrame) -> None:
    """Render High/Medium/Low risk alert card."""

    st.subheader("Risk Alert")
    if portfolio_risk.empty:
        st.info("\uc544\uc9c1 \ub9ac\uc2a4\ud06c \uc54c\ub9bc\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.")
        return

    penalties = pd.to_numeric(portfolio_risk["total_risk_penalty"], errors="coerce").fillna(0)
    high = int((penalties <= -30).sum())
    medium = int(((penalties < 0) & (penalties > -30)).sum())
    low = int((penalties == 0).sum())

    st.error(f"High Risk: {high}")
    st.warning(f"Medium Risk: {medium}")
    st.info(f"Low Risk: {low}")

    with st.expander("Risk messages", expanded=True):
        for _, row in portfolio_risk.iterrows():
            messages = row.get("risk_messages", [])
            if messages:
                st.write(f"{row['ticker']}: " + " | ".join(messages))
