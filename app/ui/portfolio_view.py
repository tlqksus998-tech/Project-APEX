from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from modules.market.master_search import search_as_dataframe
from modules.portfolio.session_state import (
    add_holding,
    get_portfolio_state,
    initialize_portfolio_state,
    remove_holding,
    set_portfolio_state,
)
from modules.utils import format_currency, format_percent


@dataclass(frozen=True)
class SearchResult:
    """Resolved portfolio search candidate."""

    name: str
    ticker: str
    market: str

    @property
    def label(self) -> str:
        """Return the label shown in the search result selector."""

        return f"{self.name} ({self.ticker})"


K_PORTFOLIO_INPUT = "Portfolio Input"
K_SEARCH = "\uc885\ubaa9 \uac80\uc0c9"
K_SEARCH_PLACEHOLDER = "\uc0bc\uc131, SK\ud558\uc774\ub2c9\uc2a4, TIGER, SOXL, NVIDIA, MU"
K_SEARCH_RESULT = "\uac80\uc0c9 \uacb0\uacfc \uc120\ud0dd"
K_RESULT_COUNT = "\uac80\uc0c9 \uacb0\uacfc"
K_QUANTITY = "\ubcf4\uc720\uc218\ub7c9"
K_AVERAGE_PRICE = "\ud3c9\uade0\ub2e8\uac00"
K_ADD = "\ud3ec\ud2b8\ud3f4\ub9ac\uc624\uc5d0 \ucd94\uac00"
K_CURRENT = "\ud604\uc7ac \ud3ec\ud2b8\ud3f4\ub9ac\uc624"
K_DELETE = "\uc885\ubaa9 \uc0ad\uc81c"
K_DELETE_SELECT = "\uc0ad\uc81c\ud560 \uc885\ubaa9"
K_NO_RESULTS = "\uac80\uc0c9 \uacb0\uacfc\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \uc885\ubaa9\uba85\uc774\ub098 \ud2f0\ucee4\ub97c \ud655\uc778\ud574\uc8fc\uc138\uc694."
K_EMPTY = "\uc544\uc9c1 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \uc885\ubaa9\uc744 \uac80\uc0c9\ud574 \ucd94\uac00\ud574\ubcf4\uc138\uc694."
K_LOAD_SAMPLE = "\uc0d8\ud50c \ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ubd88\ub7ec\uc624\uae30"


def build_search_results(query: str) -> list[SearchResult]:
    """Build normalized Korean/US stock and ETF search results."""

    clean_query = str(query or "").strip()
    if not clean_query:
        return []

    data = search_as_dataframe(clean_query, limit=30)
    results: list[SearchResult] = []
    for row in data.itertuples(index=False):
        results.append(SearchResult(name=str(row.name), ticker=str(row.ticker), market=str(row.market)))
    return results


def render_portfolio_input(sample_df: pd.DataFrame) -> pd.DataFrame:
    """Render search-first portfolio input backed by Streamlit session state."""

    initialize_portfolio_state(sample_df)
    st.subheader(K_PORTFOLIO_INPUT)
    if st.session_state.pop("portfolio_flash", None):
        st.success("\ud3ec\ud2b8\ud3f4\ub9ac\uc624\uac00 \uac31\uc2e0\ub418\uc5c8\uc2b5\ub2c8\ub2e4.")

    query = st.text_input(K_SEARCH, placeholder=K_SEARCH_PLACEHOLDER, key="portfolio_search_query")
    results = build_search_results(query)
    selected_result: SearchResult | None = None

    if query and not results:
        st.warning(K_NO_RESULTS)
    if results:
        st.caption(f"{K_RESULT_COUNT}: {len(results)}\uac1c")
        labels = [result.label for result in results]
        selected_label = st.selectbox(K_SEARCH_RESULT, labels, key="portfolio_search_result")
        selected_result = results[labels.index(selected_label)]

    col_qty, col_price, col_add = st.columns([0.22, 0.28, 0.5], vertical_alignment="bottom")
    quantity = col_qty.number_input(K_QUANTITY, min_value=0.0, value=1.0, step=1.0, key="portfolio_add_quantity")
    avg_price = col_price.number_input(K_AVERAGE_PRICE, min_value=0.0, value=0.0, step=100.0, key="portfolio_add_avg_price")
    if col_add.button(K_ADD, width="stretch", disabled=selected_result is None, key="portfolio_add_button"):
        if selected_result is None:
            st.warning(K_NO_RESULTS)
        else:
            success, message = add_holding(selected_result.name, selected_result.ticker, quantity, avg_price)
            if success:
                st.session_state["portfolio_flash"] = message
                st.rerun()
            else:
                st.warning(message)

    portfolio = get_portfolio_state()
    st.markdown(f"**{K_CURRENT}**")
    if portfolio.empty:
        st.info(K_EMPTY)
        if st.button(K_LOAD_SAMPLE, width="stretch", key="portfolio_load_sample"):
            set_portfolio_state(sample_df)
            st.session_state["portfolio_flash"] = K_LOAD_SAMPLE
            st.rerun()
        return portfolio

    edited = st.data_editor(
        portfolio,
        num_rows="fixed",
        width="stretch",
        hide_index=True,
        disabled=["name", "ticker"],
        column_config={
            "name": st.column_config.TextColumn("Name", required=True),
            "ticker": st.column_config.TextColumn("Ticker", required=True),
            "quantity": st.column_config.NumberColumn(K_QUANTITY, min_value=0.0, step=1.0, required=True),
            "avg_price": st.column_config.NumberColumn(K_AVERAGE_PRICE, min_value=0.0, step=1.0, required=True),
        },
        key="portfolio_editor",
    )
    normalized_before = portfolio.reset_index(drop=True)
    set_portfolio_state(edited)
    normalized_after = get_portfolio_state().reset_index(drop=True)
    if not normalized_before.equals(normalized_after):
        st.session_state["portfolio_flash"] = "Portfolio updated."
        st.rerun()

    refreshed = get_portfolio_state()
    delete_options = [f"{row.name} ({row.ticker})" for row in refreshed.itertuples(index=False)]
    if delete_options:
        col_select, col_delete = st.columns([0.75, 0.25], vertical_alignment="bottom")
        selected_delete = col_select.selectbox(K_DELETE_SELECT, delete_options, key="portfolio_delete_select")
        if col_delete.button(K_DELETE, width="stretch", key="portfolio_delete_button"):
            ticker = selected_delete.rsplit("(", 1)[-1].rstrip(")")
            remove_holding(ticker)
            st.rerun()

    return get_portfolio_state()


def render_portfolio_errors(errors: list[str]) -> None:
    """Render portfolio validation warnings with friendly wording."""

    friendly = {
        "Portfolio is empty. Add at least one holding.": "\uc544\uc9c1 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \uc544\ub798\uc5d0\uc11c \uc885\ubaa9\uc744 \uac80\uc0c9\ud574 \ucd94\uac00\ud574\ubcf4\uc138\uc694.",
        "Some rows have an empty ticker or unresolved name.": "\ud2f0\ucee4\ub97c \ud655\uc778\ud560 \uc218 \uc5c6\ub294 \ud589\uc774 \uc788\uc2b5\ub2c8\ub2e4. \uc885\ubaa9\uba85\uc774\ub098 \ud2f0\ucee4\ub97c \ub2e4\uc2dc \ud655\uc778\ud574\uc8fc\uc138\uc694.",
        "Quantity must be greater than zero.": "\ubcf4\uc720\uc218\ub7c9\uc740 0\ubcf4\ub2e4 \ucee4\uc57c \ud569\ub2c8\ub2e4.",
        "Average price cannot be negative.": "\ud3c9\uade0\ub2e8\uac00\ub294 \ub9c8\uc774\ub108\uc2a4\ub85c \uc785\ub825\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    }
    for error in errors:
        st.warning(friendly.get(error, "\uc785\ub825\uac12\uc744 \ud655\uc778\ud574\uc8fc\uc138\uc694. \uc7a0\uc2dc \ud6c4 \ub2e4\uc2dc \uc2dc\ub3c4\ud574\ub3c4 \uc571\uc740 \uc885\ub8cc\ub418\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4."))


def render_metric_dashboard(metrics: dict[str, float]) -> None:
    """Render portfolio valuation metrics."""

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Invested", format_currency(metrics["total_invested"]))
    col2.metric("Current Value", format_currency(metrics["total_current_value"]))
    col3.metric("Profit / Loss", format_currency(metrics["profit_loss"]))
    col4.metric("Return", format_percent(metrics["return_rate"]))


def render_portfolio_positions(positions: pd.DataFrame) -> None:
    """Render calculated portfolio positions."""

    st.subheader("Portfolio Positions")
    display_columns = [
        "name",
        "ticker",
        "quantity",
        "avg_price",
        "current_price",
        "invested_amount",
        "current_value",
        "profit_loss",
        "return_rate",
        "weight",
        "price_source",
    ]
    if positions.empty:
        st.info("Enter at least one valid portfolio row to calculate the dashboard.")
        return
    st.dataframe(positions[display_columns], width="stretch", hide_index=True)
