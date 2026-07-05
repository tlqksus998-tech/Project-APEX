def format_currency(value: float) -> str:
    """Format a number as a compact currency-like value."""

    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    """Format a decimal ratio as a percentage string."""

    return f"{value:.2%}"
