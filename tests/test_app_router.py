from __future__ import annotations

from app.ui.router import PAGE_ROUTES, render_page, resolve_renderer
from app.ui.sidebar import MENU_ITEMS


def test_router_importable_and_menu_items_present():
    assert callable(render_page)
    assert "쉽게 보기 · 종목분석" in MENU_ITEMS
    assert "쉽게 보기 · AI 랭킹" in MENU_ITEMS
    assert "개발자 모드 · 내 투자 현황" in MENU_ITEMS


def test_router_covers_all_sidebar_menus():
    for menu in MENU_ITEMS:
        assert menu in PAGE_ROUTES
        assert callable(resolve_renderer(menu))
