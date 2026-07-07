from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.portfolio.session_state import add_holding, get_portfolio_state, set_portfolio_state


def test_more_than_five_portfolio_items_can_be_added():
    st.session_state.clear()
    set_portfolio_state(pd.DataFrame(columns=["name", "ticker", "quantity", "avg_price"]))

    for index in range(6):
        success, message = add_holding(f"Asset {index}", f"T{index:03d}", 1, 100)
        assert success, message

    assert len(get_portfolio_state()) == 6


def test_more_than_ten_portfolio_items_can_be_added():
    st.session_state.clear()
    set_portfolio_state(pd.DataFrame(columns=["name", "ticker", "quantity", "avg_price"]))

    for index in range(11):
        success, message = add_holding(f"Asset {index}", f"X{index:03d}", 1, 100)
        assert success, message

    assert len(get_portfolio_state()) == 11
