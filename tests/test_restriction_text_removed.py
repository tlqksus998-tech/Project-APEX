from __future__ import annotations

from pathlib import Path


def test_major_ui_has_no_paid_plan_messages():
    files = [
        Path("app/ui/sidebar.py"),
        Path("app/ui/brand_header.py"),
        Path("app/ui/candidate_view.py"),
        Path("app/ui/portfolio_view.py"),
        Path("app/ui/pro_gate_view.py"),
    ]
    forbidden = [
        "Current Plan",
        "Upgrade",
        "무료버전",
        "유료버전",
        "Pro 기능",
        "Pro에서",
        "최대 5개",
        "5개까지",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in files)

    for text in forbidden:
        assert text not in combined
