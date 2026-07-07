from __future__ import annotations

from modules.utils import format_currency, format_percent


def test_format_currency_and_percent():
    assert format_currency(1234567) == "1,234,567"
    assert format_percent(0.1234) == "12.34%"
