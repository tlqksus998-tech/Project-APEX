from __future__ import annotations

from modules.ranking.ai_ranking_service import DEFAULT_KOSDAQ_CANDIDATES, DEFAULT_KOSPI_CANDIDATES, DEFAULT_NASDAQ_CANDIDATES, select_candidate_pool


def test_default_candidate_pools_have_at_least_top10_capacity() -> None:
    """Each ranking market should have enough representative candidates for top 10."""

    assert len(DEFAULT_KOSPI_CANDIDATES) >= 10
    assert len(DEFAULT_KOSDAQ_CANDIDATES) >= 10
    assert len(DEFAULT_NASDAQ_CANDIDATES) >= 10


def test_select_candidate_pool_respects_limit() -> None:
    """Candidate pool selection should stay bounded for performance."""

    assert len(select_candidate_pool("KOSPI", candidate_limit=10)) <= 10
    assert len(select_candidate_pool("KOSDAQ", candidate_limit=10)) <= 10
    assert len(select_candidate_pool("NASDAQ", candidate_limit=10)) <= 10
