from __future__ import annotations

from modules.theme.theme_models import ThemeAsset

THEME_ASSETS: dict[str, list[ThemeAsset]] = {
    "반도체": [
        ThemeAsset("SK하이닉스", "000660", "KR"),
        ThemeAsset("삼성전자", "005930", "KR"),
        ThemeAsset("Micron", "MU", "US"),
        ThemeAsset("NVIDIA", "NVDA", "US"),
        ThemeAsset("Broadcom", "AVGO", "US"),
        ThemeAsset("AMD", "AMD", "US"),
        ThemeAsset("ASML", "ASML", "US"),
    ],
    "AI": [
        ThemeAsset("NVIDIA", "NVDA", "US"),
        ThemeAsset("Broadcom", "AVGO", "US"),
        ThemeAsset("Microsoft", "MSFT", "US"),
        ThemeAsset("Google", "GOOGL", "US"),
        ThemeAsset("Meta", "META", "US"),
        ThemeAsset("Amazon", "AMZN", "US"),
        ThemeAsset("Palantir", "PLTR", "US"),
    ],
    "전기차": [
        ThemeAsset("Tesla", "TSLA", "US"),
        ThemeAsset("현대차", "005380", "KR"),
        ThemeAsset("기아", "000270", "KR"),
        ThemeAsset("LG에너지솔루션", "373220", "KR"),
    ],
    "우주항공": [
        ThemeAsset("TIGER 미국우주항공", "493810", "KR"),
        ThemeAsset("Rocket Lab", "RKLB", "US"),
        ThemeAsset("Lockheed Martin", "LMT", "US"),
        ThemeAsset("Northrop Grumman", "NOC", "US"),
    ],
    "게임": [
        ThemeAsset("넥슨게임즈", "225570", "KR"),
        ThemeAsset("크래프톤", "259960", "KR"),
        ThemeAsset("엔씨소프트", "036570", "KR"),
        ThemeAsset("넷마블", "251270", "KR"),
    ],
    "바이오": [
        ThemeAsset("삼성바이오로직스", "207940", "KR"),
        ThemeAsset("셀트리온", "068270", "KR"),
        ThemeAsset("유한양행", "000100", "KR"),
    ],
    "금융": [
        ThemeAsset("KB금융", "105560", "KR"),
        ThemeAsset("신한지주", "055550", "KR"),
        ThemeAsset("하나금융지주", "086790", "KR"),
        ThemeAsset("JPMorgan", "JPM", "US"),
    ],
    "에너지": [
        ThemeAsset("Exxon Mobil", "XOM", "US"),
        ThemeAsset("Chevron", "CVX", "US"),
        ThemeAsset("한국석유", "004090", "KR"),
        ThemeAsset("S-Oil", "010950", "KR"),
    ],
    "방산": [
        ThemeAsset("한화에어로스페이스", "012450", "KR"),
        ThemeAsset("LIG넥스원", "079550", "KR"),
        ThemeAsset("Lockheed Martin", "LMT", "US"),
        ThemeAsset("Northrop Grumman", "NOC", "US"),
    ],
    "로봇": [
        ThemeAsset("레인보우로보틱스", "277810", "KR"),
        ThemeAsset("두산로보틱스", "454910", "KR"),
        ThemeAsset("Intuitive Surgical", "ISRG", "US"),
    ],
    "클라우드": [
        ThemeAsset("Amazon", "AMZN", "US"),
        ThemeAsset("Microsoft", "MSFT", "US"),
        ThemeAsset("Google", "GOOGL", "US"),
        ThemeAsset("Snowflake", "SNOW", "US"),
    ],
    "사이버보안": [
        ThemeAsset("Palo Alto Networks", "PANW", "US"),
        ThemeAsset("CrowdStrike", "CRWD", "US"),
        ThemeAsset("Cloudflare", "NET", "US"),
    ],
}


def list_themes() -> list[str]:
    """Return configured theme names."""

    return list(THEME_ASSETS.keys())


def get_theme_assets(theme: str) -> list[ThemeAsset]:
    """Return assets mapped to a theme."""

    return THEME_ASSETS.get(str(theme or ""), [])
