from __future__ import annotations

from modules.data_freshness import build_freshness_snapshot, format_timestamp, mark_analysis_run
from modules.data_freshness.freshness_models import DataFreshnessSnapshot


def test_freshness_tracker_returns_snapshot():
    analysis_time = mark_analysis_run()
    snapshot = build_freshness_snapshot(fx_rate=1381.5, fx_updated_at=analysis_time, analysis_run_at=analysis_time)

    assert isinstance(snapshot, DataFreshnessSnapshot)
    assert snapshot.fx_rate == 1381.5
    assert snapshot.analysis_run_at == analysis_time
    assert format_timestamp(snapshot.data_updated_at)


def test_freshness_format_handles_missing_timestamp():
    assert format_timestamp(None) == "확인 전"
