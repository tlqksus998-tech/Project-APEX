from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from modules.news.news_models import ThemeNewsItem, ThemeNewsResult

KST = ZoneInfo("Asia/Seoul")


def get_demo_news(theme: str, related_tickers: list[str] | None = None, reason: str = "") -> ThemeNewsResult:
    """Return clearly marked demo/fallback news for one theme."""

    tickers = related_tickers or []
    now = datetime.now(KST)
    items = [
        ThemeNewsItem(
            title=f"[Demo] {theme} 테마 주요 이슈 점검",
            source="APEX Demo",
            published_at=now,
            url="",
            summary="실제 뉴스 API가 아닌 샘플 데이터입니다. 테마 흐름을 점검하기 위한 자리표시자입니다.",
            theme=theme,
            related_tickers=tickers[:4],
            impact_level="Medium",
            sentiment_label="참고",
            is_fallback=True,
        ),
        ThemeNewsItem(
            title=f"[Sample] {theme} 관련 종목 변동성 확인 필요",
            source="APEX Sample",
            published_at=now,
            url="",
            summary="뉴스 데이터는 투자 참고자료이며 매수 지시가 아닙니다.",
            theme=theme,
            related_tickers=tickers[:4],
            impact_level="Low",
            sentiment_label="중립",
            is_fallback=True,
        ),
    ]
    return ThemeNewsResult(theme, items, now, "demo", False, True, reason or "뉴스 조회 실패 또는 미연동으로 Demo 데이터를 표시합니다.")
