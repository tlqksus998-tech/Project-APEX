from __future__ import annotations

from modules.theme.theme_mapping import get_theme_assets, list_themes


def test_theme_mapping_contains_core_themes():
    themes = list_themes()
    assert "반도체" in themes
    assert "AI" in themes
    assert "전기차" in themes


def test_theme_assets_have_name_and_ticker():
    assets = get_theme_assets("반도체")
    assert assets
    assert all(asset.name and asset.ticker for asset in assets)
