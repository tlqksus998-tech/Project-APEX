from __future__ import annotations

import streamlit as st

from modules.portfolio.input_data import get_sample_portfolio
from modules.portfolio.session_state import set_portfolio_state

K_GUIDE_TITLE = "\ucc98\uc74c \uc0ac\uc6a9\ud558\ub294 \ubd84\uc744 \uc704\ud55c 3\ubd84 \uac00\uc774\ub4dc"
K_GUIDE_BODY = "\uc885\ubaa9\uc744 \uac80\uc0c9\ud558\uace0 \uc218\ub7c9/\ud3c9\ub2e8\uc744 \uc785\ub825\ud55c \ub4a4 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\uc5d0 \ucd94\uac00\ud558\uba74 \uc624\ub298\uc758 \ud22c\uc790\ud310\ub2e8\uc774 \uc790\ub3d9\uc73c\ub85c \uac31\uc2e0\ub429\ub2c8\ub2e4."
K_LOAD_SAMPLE = "\uc0d8\ud50c \ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ubd88\ub7ec\uc624\uae30"
K_DIRECT = "\ub0b4 \ud3ec\ud2b8\ud3f4\ub9ac\uc624 \uc9c1\uc811 \uc785\ub825\ud558\uae30"
K_EMPTY = "\uc544\uc9c1 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \uc885\ubaa9\uc744 \uac80\uc0c9\ud574 \ucd94\uac00\ud574\ubcf4\uc138\uc694."


def load_sample_portfolio() -> None:
    """Load the built-in sample portfolio into session state."""

    set_portfolio_state(get_sample_portfolio())


def render_onboarding(mode: str) -> None:
    """Render first-run guide and quick action buttons."""

    if mode != "beginner":
        return

    with st.container(border=True):
        st.subheader(K_GUIDE_TITLE)
        st.write(K_GUIDE_BODY)
        st.markdown("1. **\uc885\ubaa9 \uac80\uc0c9**: \uc0bc\uc131\uc804\uc790, KORU, \ub9c8\uc774\ud06c\ub860\ucc98\ub7fc \uc785\ub825\ud569\ub2c8\ub2e4.")
        st.markdown("2. **\uc218\ub7c9/\ud3c9\ub2e8 \uc785\ub825**: \ud3c9\ub2e8\uc744 \ubaa8\ub974\uba74 0\uc73c\ub85c \ub450\uace0 \uc2dc\uc791\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.")
        st.markdown("3. **\ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ucd94\uac00**: \ucd94\uac00\ud558\uba74 \ubd84\uc11d\uc774 \uc790\ub3d9 \uac31\uc2e0\ub429\ub2c8\ub2e4.")
        st.markdown("4. **\uc624\ub298\uc758 \ud22c\uc790\ud310\ub2e8 \ud655\uc778**: Decision\uacfc \uc624\ub298 \ud574\uc57c \ud560 \ud589\ub3d9\uc744 \uba3c\uc800 \ubd05\ub2c8\ub2e4.")
        col1, col2 = st.columns(2)
        if col1.button(K_LOAD_SAMPLE, width="stretch", key="onboarding_load_sample"):
            load_sample_portfolio()
            st.rerun()
        if col2.button(K_DIRECT, width="stretch", key="onboarding_direct_input"):
            st.session_state["focus_portfolio_input"] = True
            st.info("\uc544\ub798\uc758 Portfolio Input\uc5d0\uc11c \uc885\ubaa9\uc744 \uac80\uc0c9\ud574 \ucd94\uac00\ud558\uba74 \ub429\ub2c8\ub2e4.")


def render_empty_state() -> None:
    """Render a simple empty state for users with no holdings."""

    with st.container(border=True):
        st.info(K_EMPTY)
        if st.button(K_LOAD_SAMPLE, width="stretch", key="empty_load_sample"):
            load_sample_portfolio()
            st.rerun()
