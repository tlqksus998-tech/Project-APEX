from __future__ import annotations

from app.ui.router import render_page
from app.ui.sidebar import MENU_ITEMS


def test_router_importable_and_menu_items_present():
    assert callable(render_page)
    assert "내 투자 현황" in MENU_ITEMS
    assert "테마 레이더" in MENU_ITEMS


def test_router_covers_all_sidebar_menus():
    from app.ui.router import PAGE_ROUTES

    for menu in MENU_ITEMS:
        assert menu in PAGE_ROUTES
