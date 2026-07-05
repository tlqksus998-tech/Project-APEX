from __future__ import annotations

import streamlit as st


WELCOME_TEXT = "Welcome to the Project APEX Decision Engine Foundation sprint."


def render_header(project_name: str, project_subtitle: str, sprint_name: str) -> None:
    """Render the shared page header."""

    st.title(project_name)
    st.caption(project_subtitle)
    st.write(WELCOME_TEXT)
    st.write(f"Current development stage: **{sprint_name}**")


def render_status_cards(version: str) -> None:
    """Render project status cards."""

    col1, col2, col3 = st.columns(3)
    col1.info("Stage\n\nSprint 2.5")
    col2.success("Status\n\nDecision Engine MVP")
    col3.info(f"Version\n\n{version}")
