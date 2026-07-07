from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from modules.data_providers.live_price_provider import get_live_prices
from modules.theme.theme_mapping import get_theme_assets, list_themes
from modules.theme.theme_models import ThemeStrengthResult

KST = ZoneInfo("Asia/Seoul")


def calculate_theme_strength(theme: str, use_live: bool = False) -> ThemeStrengthResult:
    """Calculate theme strength from related asset recent moves."""

    assets = get_theme_assets(theme)
    if not assets:
        return ThemeStrengthResult(theme, 0.0, 0, 0, 0, "데이터 부족", [], now_kst(), "fallback", False, True, "등록된 테마 종목이 없습니다.")
    if not use_live:
        changes = fallback_theme_changes(theme, len(assets))
        avg_change = sum(changes) / len(changes) if changes else 0.0
        return ThemeStrengthResult(
            theme=theme,
            avg_change_pct=avg_change,
            positive_count=sum(1 for value in changes if value > 0),
            negative_count=sum(1 for value in changes if value < 0),
            total_count=len(changes),
            strength_label=classify_strength(avg_change, len(changes)),
            representative_tickers=[asset.ticker for asset in assets[:5]],
            updated_at=now_kst(),
            source="fallback_snapshot",
            success=True,
            is_fallback=True,
            error_message="빠른 화면 표시를 위해 fallback snapshot 기준으로 표시합니다.",
        )
    price_results = get_live_prices([(asset.ticker, asset.name, asset.market) for asset in assets])
    valid = [item for item in price_results if item.success and not item.is_fallback]
    source = "live_provider"
    is_fallback = False
    success = True
    error = ""
    usable = valid or price_results
    if not valid:
        source = "fallback"
        is_fallback = True
        success = False
        error = "최근 가격 조회가 부족해 fallback 기준으로 표시합니다."
    changes = [item.change_pct for item in usable]
    avg_change = sum(changes) / len(changes) if changes else 0.0
    positive = sum(1 for value in changes if value > 0)
    negative = sum(1 for value in changes if value < 0)
    return ThemeStrengthResult(
        theme=theme,
        avg_change_pct=avg_change,
        positive_count=positive,
        negative_count=negative,
        total_count=len(usable),
        strength_label=classify_strength(avg_change, len(usable)),
        representative_tickers=[asset.ticker for asset in assets[:5]],
        updated_at=now_kst(),
        source=source,
        success=success,
        is_fallback=is_fallback,
        error_message=error,
    )


def calculate_all_theme_strengths(use_live: bool = False) -> list[ThemeStrengthResult]:
    """Calculate strengths for all configured themes."""

    return [calculate_theme_strength(theme, use_live=use_live) for theme in list_themes()]


def classify_strength(avg_change_pct: float, count: int = 1) -> str:
    """Classify theme strength."""

    if count <= 0:
        return "데이터 부족"
    if avg_change_pct >= 0.015:
        return "강한 강세"
    if avg_change_pct >= 0.003:
        return "강세"
    if avg_change_pct > -0.003:
        return "중립"
    if avg_change_pct > -0.015:
        return "약세"
    return "강한 약세"


def now_kst() -> datetime:
    """Return current KST timestamp."""

    return datetime.now(KST)


def fallback_theme_changes(theme: str, count: int) -> list[float]:
    """Return deterministic pseudo changes for fast fallback display."""

    if count <= 0:
        return []
    seed = sum(ord(char) for char in theme)
    values = []
    for index in range(count):
        raw = ((seed + index * 17) % 41) - 20
        values.append(raw / 1000)
    return values
