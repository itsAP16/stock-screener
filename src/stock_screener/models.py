"""Data models used by the stock screener."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StockFinancials:
    """Snapshot of a company's key valuation metrics."""

    ticker: str
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    dividend_yield: Optional[float]
    market_cap: Optional[float]

    def as_row(self) -> list[Optional[float]]:
        """Return the financial metrics as a list suitable for table output."""

        return [
            self.ticker,
            self.pe_ratio,
            self.pb_ratio,
            self.dividend_yield,
            self.market_cap,
        ]
