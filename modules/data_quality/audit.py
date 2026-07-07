from __future__ import annotations

from pathlib import Path


def run_data_quality_audit() -> dict[str, object]:
    """Run a lightweight static audit for risky sample/fallback score paths."""

    root = Path(__file__).resolve().parents[2]
    targets = [
        root / "modules" / "ranking" / "ai_ranking_service.py",
        root / "app" / "ui" / "beginner_ranking_view.py",
        root / "app" / "ui" / "stock_analysis_view.py",
        root / "modules" / "screening" / "candidate_screener.py",
    ]
    findings: list[str] = []
    for path in targets:
        try:
            source = path.read_text(encoding="utf-8").lower()
        except OSError:
            continue
        if "fallback" in source and "is_decision_allowed" not in source and path.name == "ai_ranking_service.py":
            findings.append(f"{path.name}: fallback guard 확인 필요")
        if "screen_today_candidates" in source and path.name == "beginner_ranking_view.py":
            findings.append("beginner_ranking_view.py: legacy candidate score path 사용")
    return {
        "checked_files": [str(path) for path in targets],
        "findings": findings,
        "passed": not findings,
    }
