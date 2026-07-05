from __future__ import annotations

import contextlib
import io
from typing import Callable, TypeVar

import pandas as pd
import streamlit as st
import yfinance as yf


DEFAULT_TTL_SECONDS = 600
F = TypeVar("F", bound=Callable[..., object])


def cache_data(ttl: int = DEFAULT_TTL_SECONDS) -> Callable[[F], F]:
    """Return a Streamlit cache decorator with one extension point for future file caching."""

    return st.cache_data(ttl=ttl, show_spinner=False)


@cache_data()
def cached_yfinance_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """Fetch yfinance history through Streamlit cache_data."""

    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        history = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
    if history is None:
        return pd.DataFrame()
    return history.copy()
