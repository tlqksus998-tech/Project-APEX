from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CashPosition:
    """KRW/USD cash settings for portfolio operation."""

    krw_cash: float = 0.0
    usd_cash: float = 0.0
    usdkrw: float = 1380.0

    @property
    def total_cash_krw(self) -> float:
        """Return total cash converted to KRW."""

        return max(self.krw_cash, 0.0) + (max(self.usd_cash, 0.0) * max(self.usdkrw, 0.0))


def calculate_total_cash(krw_cash: float = 0.0, usd_cash: float = 0.0, usdkrw: float = 1380.0) -> float:
    """Calculate total cash in KRW."""

    return CashPosition(krw_cash, usd_cash, usdkrw).total_cash_krw


def calculate_investable_cash(total_cash_krw: float, reserve_ratio: float = 0.10) -> float:
    """Calculate rough additional investable cash after a cash reserve."""

    return max(float(total_cash_krw or 0.0) * max(0.0, 1.0 - reserve_ratio), 0.0)
