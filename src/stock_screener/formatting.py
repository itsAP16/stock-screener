"""Utility helpers for presenting numeric values."""
from __future__ import annotations


def format_number(value: float | None) -> str:
    """Return a human-friendly string representation of ``value``.

    ``None`` values are rendered as ``"-"`` to match console output expectations.
    Large absolute values are formatted with comma separators and two decimal
    places. Small values retain up to four decimal places to avoid rounding
    significant fractional components to zero.
    """

    if value is None:
        return "-"
    if abs(value) >= 1:
        return f"{value:,.2f}"
    return f"{value:.4f}"
