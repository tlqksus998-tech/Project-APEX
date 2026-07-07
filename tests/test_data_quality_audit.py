from __future__ import annotations

from modules.data_quality import run_trading_readiness_audit


def test_trading_readiness_audit_runs() -> None:
    """Trading readiness audit should be executable."""

    result = run_trading_readiness_audit()
    assert result.checked_items
    assert isinstance(result.passed, bool)
