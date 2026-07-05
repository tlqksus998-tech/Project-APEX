from __future__ import annotations


def build_recommendations(decision: str) -> list[str]:
    """Return action recommendations for a decision code."""

    normalized = str(decision or "HOLD").upper()
    if normalized in {"STRONG_BUY", "BUY"}:
        return [
            "\u2022 \uc2e0\uaddc\ub9e4\uc218 : \ubd84\ud560\ub9e4\uc218\ub97c \uad8c\uc7a5\ud569\ub2c8\ub2e4.",
            "\u2022 \ubcf4\uc720 : \uc720\uc9c0",
            "\u2022 \ucd94\uac00\ub9e4\uc218 : \ub9ac\uc2a4\ud06c \ud655\uc778 \ud6c4 \uc18c\uc561\uc73c\ub85c \uac80\ud1a0",
        ]
    if normalized == "HOLD":
        return [
            "\u2022 \uc2e0\uaddc\ub9e4\uc218 : \ubcf4\ub958",
            "\u2022 \ubcf4\uc720 : \uc720\uc9c0",
            "\u2022 \ucd94\uac00\ub9e4\uc218 : 20\uc77c\uc120 \uc9c0\uc9c0 \ud655\uc778 \ud6c4 \uac80\ud1a0",
        ]
    if normalized == "REDUCE":
        return [
            "\u2022 \uc2e0\uaddc\ub9e4\uc218 : \ubcf4\ub958",
            "\u2022 \ubcf4\uc720 : \uc77c\ubd80 \ube44\uc911 \ucd95\uc18c \uac80\ud1a0",
            "\u2022 \ucd94\uac00\ub9e4\uc218 : \uae08\uc9c0",
        ]
    return [
        "\u2022 \uc2e0\uaddc\ub9e4\uc218 : \ubcf4\ub958",
        "\u2022 \ubcf4\uc720 : \uc190\uc808 \ub610\ub294 \ube44\uc911\ucd95\uc18c \uac80\ud1a0",
        "\u2022 \ucd94\uac00\ub9e4\uc218 : \uae08\uc9c0",
    ]
