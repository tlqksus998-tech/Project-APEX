from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.ui.design_system import load_theme
from app.ui.page_context import PageContext
from app.ui.router import render_page
from app.ui.sidebar import render_cash_inputs, render_market_controls, render_sidebar, render_user_mode, render_version_footer
from modules.data_freshness import build_freshness_snapshot
from modules.market.macro_provider import build_macro_brief
from modules.market.sentiment_provider import get_fear_greed_placeholder
from modules.portfolio.session_state import initialize_portfolio_state

K_PAGE_TITLE = "오늘의 투자판단"


def init_app() -> None:
    """Initialize Streamlit page and shared styling."""

    st.set_page_config(page_title=K_PAGE_TITLE, layout="wide")
    load_theme()
    initialize_portfolio_state()


def build_page_context() -> PageContext:
    """Collect sidebar inputs and shared runtime data for page renderers."""

    selected_menu = render_sidebar()
    user_mode = render_user_mode()
    period, interval = render_market_controls()
    cash = render_cash_inputs()
    render_version_footer()

    macro_brief = build_macro_brief()
    sentiment = get_fear_greed_placeholder()
    freshness = build_freshness_snapshot(
        fx_rate=cash.usdkrw,
        fx_updated_at=st.session_state.get("fx_updated_at"),
        fx_source=st.session_state.get("fx_source", "manual"),
        price_updated_at=macro_brief.updated_at,
        macro_updated_at=macro_brief.updated_at,
    )
    return PageContext(
        selected_menu=selected_menu,
        user_mode=user_mode,
        beginner_mode=user_mode == "beginner",
        period=period,
        interval=interval,
        cash=cash,
        macro_brief=macro_brief,
        sentiment=sentiment,
        freshness=freshness,
    )


def main() -> None:
    """Run Project APEX."""

    init_app()
    context = build_page_context()
    render_page(context)


if __name__ == "__main__":
    main()
