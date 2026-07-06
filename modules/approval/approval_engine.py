from __future__ import annotations

from modules.approval.approval_models import ApprovalDecision, ApprovalResult


def create_placeholder_approval(ticker: str) -> ApprovalResult:
    """Return a conservative placeholder approval result."""

    return ApprovalResult(ticker=ticker, decision=ApprovalDecision.WAIT, reasons=["Portfolio approval engine foundation only."])
