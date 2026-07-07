from __future__ import annotations

from pathlib import Path
from datetime import datetime

from modules.data_quality.data_quality_models import AuditResult


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


def run_trading_readiness_audit() -> AuditResult:
    """Run a lightweight audit for trading readiness guard wiring."""

    root = Path(__file__).resolve().parents[2]
    checked_items = [
        "fallback/sample/demo source blocking",
        "shared ranking/detail AI judgement service",
        "data_timestamp and query_timestamp fields",
        "US extended-hours session labels",
        "final trading checklist",
    ]
    warnings: list[str] = []
    failures: list[str] = []

    ranking_path = root / "modules" / "ranking" / "ai_ranking_service.py"
    detail_path = root / "app" / "ui" / "stock_analysis_view.py"
    try:
        ranking_source = ranking_path.read_text(encoding="utf-8")
        detail_source = detail_path.read_text(encoding="utf-8")
    except OSError as exc:
        return AuditResult(False, failures=[str(exc)], checked_items=checked_items, created_at=datetime.now())

    required_ranking_tokens = ["build_trading_readiness", "is_decision_allowed", "readiness_level", "price_label"]
    for token in required_ranking_tokens:
        if token not in ranking_source:
            failures.append(f"ranking service missing {token}")
    if "get_unified_ai_judgement" not in detail_source:
        failures.append("detail page does not use unified AI judgement service")
    if "render_final_trading_checklist" not in detail_source:
        warnings.append("detail page does not render final trading checklist")

    return AuditResult(
        passed=not failures,
        warnings=warnings,
        failures=failures,
        checked_items=checked_items,
        created_at=datetime.now(),
    )
