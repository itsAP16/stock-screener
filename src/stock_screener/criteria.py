"""Filtering criteria used to decide whether a stock passes the screen."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StockFilterCriteria:
    """Filter configuration for the stock screener."""

    max_pe_ratio: Optional[float] = None
    max_pb_ratio: Optional[float] = None
    min_dividend_yield: Optional[float] = None
    min_market_cap: Optional[float] = None

    def matches(self, financials: "StockFinancials") -> bool:
        """Return ``True`` if the provided financials satisfy all configured filters."""

        from .models import StockFinancials

        if self.max_pe_ratio is not None:
            if financials.pe_ratio is None or financials.pe_ratio > self.max_pe_ratio:
                return False

        if self.max_pb_ratio is not None:
            if financials.pb_ratio is None or financials.pb_ratio > self.max_pb_ratio:
                return False

        if self.min_dividend_yield is not None:
            if (
                financials.dividend_yield is None
                or financials.dividend_yield < self.min_dividend_yield
            ):
                return False

        if self.min_market_cap is not None:
            if (
                financials.market_cap is None
                or financials.market_cap < self.min_market_cap
            ):
                return False

        return True
