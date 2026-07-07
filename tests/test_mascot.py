from __future__ import annotations

from app.ui.mascot import get_mascot_for_signal, normalize_mascot_role, render_mascot_image, resolve_mascot_path, should_show_mascot


def test_mascot_module_importable_and_missing_asset_safe() -> None:
    """Mascot asset lookup should not fail when image files are not present."""

    path = resolve_mascot_path("cabbage", "small")
    assert path is None or path.exists()


def test_mascot_role_normalization() -> None:
    """Unknown roles should use the neutral tofu pouch mascot."""

    assert normalize_mascot_role("cabbage") == "cabbage"
    assert normalize_mascot_role("green") == "cabbage"
    assert normalize_mascot_role("brown") == "mushroom"
    assert normalize_mascot_role("beige") == "tofu_pouch"
    assert normalize_mascot_role("yellow") == "tofu_pouch"
    assert normalize_mascot_role("red") == "meat"
    assert normalize_mascot_role("unknown") == "tofu_pouch"


def test_should_show_mascot_only_for_beginner_mode() -> None:
    """Mascot should be limited to beginner surfaces by default."""

    assert should_show_mascot(beginner_mode=True)
    assert not should_show_mascot(beginner_mode=False)
    assert not should_show_mascot(beginner_mode=True, compact=True)


def test_get_mascot_for_signal_shape() -> None:
    """Signal mapping should return the fields used by the UI layer."""

    mascot = get_mascot_for_signal("BUY")
    assert {"role", "name", "label", "tone", "message"}.issubset(mascot)
    assert mascot["message"]


def test_render_mascot_image_missing_asset_does_not_crash() -> None:
    """Rendering should fall back to text when image assets are missing."""

    render_mascot_image("tofu_pouch", size="small", animated=False)
