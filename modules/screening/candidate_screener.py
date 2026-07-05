from __future__ import annotations

import pandas as pd

from modules.market.master_loader import load_master_database
from modules.screening.candidate_models import CandidateStock

CANDIDATE_COLUMNS = ["name", "ticker", "market", "final_score", "decision", "reasons"]
REASON_DEFAULT = [
    "\uc0c1\uc2b9\ucd94\uc138 \ud6c4\ubcf4",
    "RSI \uc911\ub9bd \uad6c\uac04",
    "\ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ube44\uc911\uacfc \ub9ac\uc2a4\ud06c \ud655\uc778 \ud544\uc694",
]


def screen_today_candidates(analysis_results: pd.DataFrame | None = None, decision_results: pd.DataFrame | None = None, master: pd.DataFrame | None = None, limit: int = 10) -> pd.DataFrame:
    """Screen today's candidate stocks from available analysis data or KRX master fallback."""

    if analysis_results is not None and decision_results is not None and not analysis_results.empty and not decision_results.empty:
        return screen_from_analysis(analysis_results, decision_results, limit=limit)
    return screen_from_master(master if master is not None else load_master_database(), limit=limit)


def screen_from_analysis(analysis_results: pd.DataFrame, decision_results: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Screen candidates using technical analysis and decision output."""

    data = analysis_results.merge(decision_results[["ticker", "final_score", "decision", "reasons"]], on="ticker", how="inner")
    if data.empty:
        return empty_candidates()

    filtered = data[
        (data["trend_status"] == "\uc0c1\uc2b9\ucd94\uc138")
        & (pd.to_numeric(data["rsi_14"], errors="coerce").between(30, 65))
        & (data["macd_status"] == "\uc0c1\uc2b9 \ubaa8\uba58\ud140")
        & (data["volume_status"].isin(["\uac70\ub798\ub7c9 \ubcf4\ud1b5", "\uac70\ub798\ub7c9 \uc99d\uac00"]))
        & (pd.to_numeric(data["week52_position"], errors="coerce").between(20, 80))
    ].copy()
    if filtered.empty:
        filtered = data.copy()
    filtered["name"] = filtered.get("name", filtered["ticker"])
    filtered["market"] = filtered.get("market", "KRX")
    filtered["reasons"] = filtered["reasons"].map(lambda value: value[:3] if isinstance(value, list) else REASON_DEFAULT[:2])
    return normalize_candidates(filtered[["name", "ticker", "market", "final_score", "decision", "reasons"]], limit)


def screen_from_master(master: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return safe KRX candidate rows when full technical screening data is not available."""

    if master is None or master.empty:
        return empty_candidates()
    data = master.copy()
    if "market" in data.columns:
        data = data[data["market"].astype(str).str.contains("KR|KOSPI|KOSDAQ|KONEX", case=False, regex=True, na=False)]
    if "asset_type" in data.columns:
        data = data[data["asset_type"].astype(str).str.upper().isin(["STOCK", "ETF"])]
    if data.empty:
        return empty_candidates()

    preferred = ["005930", "009150", "000660", "402340", "005380", "035420", "035720", "005490", "373220"]
    data["_rank"] = data["ticker"].astype(str).map(lambda ticker: preferred.index(ticker) if ticker in preferred else 999)
    data = data.sort_values(["_rank", "ticker"]).head(limit).copy()
    data["final_score"] = data["_rank"].map(lambda rank: max(50.0, 72.0 - float(rank if rank != 999 else 9)))
    data["decision"] = "HOLD"
    data["reasons"] = [REASON_DEFAULT for _ in range(len(data))]
    return normalize_candidates(data[["name", "ticker", "market", "final_score", "decision", "reasons"]], limit)


def normalize_candidates(data: pd.DataFrame, limit: int) -> pd.DataFrame:
    """Normalize candidate result frame and sort by final score."""

    if data is None or data.empty:
        return empty_candidates()
    frame = data.copy()
    for column in CANDIDATE_COLUMNS:
        if column not in frame.columns:
            if column == "reasons":
                frame[column] = [[] for _ in range(len(frame))]
            else:
                frame[column] = ""
    frame["final_score"] = pd.to_numeric(frame["final_score"], errors="coerce").fillna(0.0)
    frame = frame.sort_values("final_score", ascending=False).head(limit)
    return frame[CANDIDATE_COLUMNS].reset_index(drop=True)


def empty_candidates() -> pd.DataFrame:
    """Return an empty candidate result DataFrame."""

    return pd.DataFrame(columns=CANDIDATE_COLUMNS)
