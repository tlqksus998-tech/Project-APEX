from __future__ import annotations

from pathlib import Path

import streamlit as st

THEME_PATH = Path(__file__).resolve().parents[1] / "styles" / "theme.css"

BADGE_CLASS = {
    "BUY APPROVED": "positive",
    "STRONG_BUY": "positive",
    "BUY": "positive",
    "WATCH": "info",
    "Strong Watch": "positive",
    "Watch": "info",
    "HOLD": "neutral",
    "WAIT": "neutral",
    "Wait": "neutral",
    "REDUCE": "warning",
    "DO NOT BUY": "negative",
    "SELL": "negative",
    "Avoid": "negative",
    "High Risk": "negative",
    "Medium Risk": "warning",
    "Low Risk": "positive",
    "Live": "positive",
    "Demo": "neutral",
    "Placeholder": "muted",
}


def load_theme() -> None:
    """Load Project APEX CSS theme into Streamlit."""

    try:
        css = THEME_PATH.read_text(encoding="utf-8")
    except OSError:
        return
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def badge(label: str) -> str:
    """Return HTML for a status badge."""

    badge_type = BADGE_CLASS.get(str(label), "muted")
    return f'<span class="apex-badge badge-{badge_type}">{label}</span>'


def render_badge(label: str) -> None:
    """Render a status badge."""

    st.markdown(badge(label), unsafe_allow_html=True)


def section_title(title: str, description: str = "") -> None:
    """Render a consistent section title."""

    desc = f"<p>{description}</p>" if description else ""
    st.markdown(f'<div class="apex-section-title"><h2>{title}</h2>{desc}</div>', unsafe_allow_html=True)


def metric_card(title: str, value: str, subtitle: str = "", tone: str = "info") -> str:
    """Return HTML for a premium KPI card."""

    safe_tone = tone if tone in {"positive", "neutral", "warning", "negative", "info"} else "info"
    return (
        f'<div class="apex-kpi-card {safe_tone}">'
        f'<div class="label">{title}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="sub">{subtitle}</div>'
        '</div>'
    )


def render_metric_grid(cards: list[tuple[str, str, str, str]], columns: int = 4) -> None:
    """Render KPI cards in rows."""

    if not cards:
        return
    for start in range(0, len(cards), columns):
        cols = st.columns(columns)
        for col, card in zip(cols, cards[start:start + columns]):
            col.markdown(metric_card(*card), unsafe_allow_html=True)
