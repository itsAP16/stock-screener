"""Data models used by the stock screener."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence


@dataclass(frozen=True)
class StockFinancials:
    """Snapshot of a company's key valuation metrics.

    The ``price_history`` attribute can be used to store a sequence of
    ``(date, price)`` pairs—such as daily closing prices—to enable
    time-series analysis alongside the point-in-time metrics.
    """

    ticker: str
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    dividend_yield: Optional[float]
    market_cap: Optional[float]
    price_history: Optional[Sequence[tuple[date, float]]] = None

    def metadata(self) -> list[Optional[float] | str]:
        """Return only the point-in-time metrics for tabular display."""

        return [
            self.ticker,
            self.pe_ratio,
            self.pb_ratio,
            self.dividend_yield,
            self.market_cap,
        ]

