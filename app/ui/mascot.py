from __future__ import annotations

from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MASCOT_DIR = PROJECT_ROOT / "assets" / "mascot"

ROLE_ALIASES = {
    "green": "cabbage",
    "brown": "mushroom",
    "beige": "tofu_pouch",
    "yellow": "tofu_pouch",
    "red": "meat",
}

MASCOT_ASSETS: dict[str, dict[str, str]] = {
    "cabbage": {
        "small": "turtle_cabbage_small.png",
        "medium": "turtle_cabbage_big.png",
        "large": "turtle_cabbage_big.png",
    },
    "mushroom": {
        "small": "turtle_mushroom_small.png",
        "medium": "turtle_mushroom_big.png",
        "large": "turtle_mushroom_big.png",
    },
    "tofu_pouch": {
        "small": "turtle_tofu_pouch_small.png",
        "medium": "turtle_tofu_pouch_big.png",
        "large": "turtle_tofu_pouch_big.png",
    },
    "meat": {
        "small": "turtle_meat_small.png",
        "medium": "turtle_meat_big.png",
        "large": "turtle_meat_big.png",
    },
}

MASCOT_WIDTHS = {
    "small": 72,
    "medium": 112,
    "large": 160,
}

ROLE_NAMES = {
    "cabbage": "배추거북이",
    "mushroom": "버섯거북이",
    "tofu_pouch": "유부거북이",
    "meat": "고기거북이",
}

ROLE_LABELS = {
    "cabbage": "배추거북이 안정 안내",
    "mushroom": "버섯거북이 관찰 안내",
    "tofu_pouch": "유부거북이 기본 안내",
    "meat": "고기거북이 주의 안내",
}

ROLE_TONES = {
    "cabbage": "positive",
    "mushroom": "neutral",
    "tofu_pouch": "info",
    "meat": "negative",
}

CABBAGE_SIGNALS = {"BUY_APPROVED", "STRONG_BUY", "BUY", "HOLD"}
MUSHROOM_SIGNALS = {"WATCH", "INTEREST", "REENTRY_CANDIDATE"}
TOFU_POUCH_SIGNALS = {"WAIT", "NEUTRAL", "UNKNOWN"}
MEAT_SIGNALS = {"REDUCE", "SELL", "DO_NOT_BUY"}


def normalize_signal(signal: str | None) -> str:
    """Normalize signal text across spaces, hyphens, and underscores."""

    if signal is None:
        return "UNKNOWN"
    return str(signal).strip().upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def normalize_mascot_role(role: str | None) -> str:
    """Return a supported Shabu Turtle role key."""

    safe_role = str(role or "").strip().lower().replace("-", "_").replace(" ", "_")
    safe_role = ROLE_ALIASES.get(safe_role, safe_role)
    if safe_role in MASCOT_ASSETS:
        return safe_role
    return "tofu_pouch"


def get_mascot_for_signal(signal: str | None) -> dict[str, str]:
    """Map an investment signal to one of the four Shabu Turtle characters."""

    normalized = normalize_signal(signal)
    if normalized in CABBAGE_SIGNALS:
        role = "cabbage"
        message = "배추거북이가 보기엔 현재 흐름은 비교적 안정적입니다. 다만 한 번에 매수하기보다는 분할 접근이 좋습니다."
    elif normalized in MUSHROOM_SIGNALS:
        role = "mushroom"
        message = "버섯거북이는 이 종목을 관심 목록에 두고 조금 더 지켜보는 쪽을 안내합니다."
    elif normalized in MEAT_SIGNALS:
        role = "meat"
        message = "고기거북이가 주의 신호를 알려드려요. 지금은 추가매수보다 리스크 관리가 우선입니다."
    else:
        role = "tofu_pouch"
        message = "유부거북이가 천천히 안내해드릴게요. 지금은 서두르지 말고 흐름을 조금 더 확인해 보세요."

    return {
        "role": role,
        "name": ROLE_NAMES[role],
        "label": ROLE_LABELS[role],
        "tone": ROLE_TONES[role],
        "message": message,
    }


def resolve_mascot_path(role: str, size: str = "small") -> Path | None:
    """Resolve a mascot image path, falling back to the group image when available."""

    safe_role = normalize_mascot_role(role)
    safe_size = size if size in MASCOT_WIDTHS else "small"
    candidate = MASCOT_DIR / MASCOT_ASSETS[safe_role][safe_size]
    if candidate.exists():
        return candidate

    group_path = MASCOT_DIR / "turtle_group.png"
    if group_path.exists():
        return group_path
    return None


def render_mascot_image(role: str, size: str = "small", animated: bool = False) -> None:
    """Render mascot image or a safe text fallback when no image asset exists."""

    safe_role = normalize_mascot_role(role)
    safe_size = size if size in MASCOT_WIDTHS else "small"
    image_path = resolve_mascot_path(safe_role, safe_size)
    width = MASCOT_WIDTHS[safe_size]
    css_class = "apex-mascot-float" if animated else ""

    if image_path is not None:
        st.image(str(image_path), width=width, caption=ROLE_LABELS[safe_role])
        return

    st.markdown(
        f"""
        <div class="apex-mascot-placeholder {css_class} mascot-{safe_role}">
            <div class="apex-mascot-face">샤부</div>
            <div class="apex-mascot-mini-label">{ROLE_NAMES[safe_role]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mascot_message(message: str, role: str = "tofu_pouch", tone: str = "info") -> None:
    """Render a compact mascot guide card with a short speech bubble."""

    safe_role = normalize_mascot_role(role)
    safe_tone = tone if tone in {"positive", "neutral", "warning", "negative", "info"} else ROLE_TONES[safe_role]
    with st.container(border=True):
        cols = st.columns([0.18, 0.82])
        with cols[0]:
            render_mascot_image(safe_role, size="small", animated=True)
        with cols[1]:
            st.markdown(
                f"""
                <div class="apex-mascot-bubble mascot-bubble-{safe_tone}">
                    <strong>{ROLE_NAMES[safe_role]} 안내</strong>
                    <p>{message}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_empty_portfolio_mascot() -> None:
    """Render beginner guidance when the portfolio is empty."""

    render_mascot_message(
        "아직 등록된 보유종목이 없습니다. 유부거북이가 처음 시작 순서를 안내해드릴게요.",
        role="tofu_pouch",
        tone="info",
    )


def render_home_mascot(status: str) -> None:
    """Render a home-level mascot message based on the current dashboard status."""

    mascot = get_mascot_for_signal(status)
    render_mascot_message(mascot["message"], role=mascot["role"], tone=mascot["tone"])


def should_show_mascot(beginner_mode: bool, compact: bool = False) -> bool:
    """Return whether the mascot should be shown for the current screen."""

    return bool(beginner_mode and not compact)
