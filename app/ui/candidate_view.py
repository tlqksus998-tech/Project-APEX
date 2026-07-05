from __future__ import annotations

import pandas as pd
import streamlit as st

K_TITLE = "\uc624\ub298\uc758 \uad00\uc2ec \ud6c4\ubcf4"
K_NOTICE = "\uc870\uac74\uc5d0 \ub9de\ub294 \uad00\uc2ec \ud6c4\ubcf4\uc774\uba70, \ucd5c\uc885 \ub9e4\uc218 \uc5ec\ubd80\ub294 \ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ube44\uc911\uacfc \ub9ac\uc2a4\ud06c\ub97c \ud568\uaed8 \ud655\uc778\ud558\uc138\uc694."
K_EMPTY = "\ud45c\uc2dc\ud560 \uad00\uc2ec \ud6c4\ubcf4\uac00 \uc544\uc9c1 \uc5c6\uc2b5\ub2c8\ub2e4. KRX \uc885\ubaa9 DB\ub97c \uc0c8\ub85c\uace0\uce68\ud558\uac70\ub098 \uc7a0\uc2dc \ud6c4 \ub2e4\uc2dc \ud655\uc778\ud558\uc138\uc694."


def render_candidate_stocks(candidates: pd.DataFrame) -> None:
    """Render today's candidate stocks section."""

    st.subheader(K_TITLE)
    st.caption(K_NOTICE)
    if candidates is None or candidates.empty:
        st.info(K_EMPTY)
        return
    display = candidates.copy()
    display["reasons"] = display["reasons"].map(format_reasons)
    display = display.rename(
        columns={
            "name": "\uc885\ubaa9\uba85",
            "ticker": "\ud2f0\ucee4",
            "final_score": "\uc810\uc218",
            "decision": "\ud310\ub2e8",
            "reasons": "\uc8fc\uc694 \uc774\uc720",
        }
    )
    columns = ["\uc885\ubaa9\uba85", "\ud2f0\ucee4", "\uc810\uc218", "\ud310\ub2e8", "\uc8fc\uc694 \uc774\uc720"]
    st.dataframe(display[[column for column in columns if column in display.columns]], width="stretch", hide_index=True)


def format_reasons(value: object) -> str:
    """Format reason list for table display."""

    if isinstance(value, list):
        return " | ".join(str(item) for item in value[:3])
    return str(value or "")
