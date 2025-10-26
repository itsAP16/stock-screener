"""Core abstractions for the data access layer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Iterator

from ..models import StockFinancials


@dataclass(frozen=True)
class FetchResult:
    """Result returned when attempting to fetch data for a ticker."""

    ticker: str
    financials: StockFinancials | None
    error: str | None = None


class DataSource(ABC):
    """Abstract interface for retrieving :class:`StockFinancials`."""

    @abstractmethod
    def fetch(self, ticker: str) -> FetchResult:
        """Retrieve financial data for ``ticker``."""

    def fetch_many(self, tickers: Iterable[str]) -> Iterator[FetchResult]:
        """Retrieve data for multiple ``tickers`` in sequence."""

        for ticker in tickers:
            yield self.fetch(ticker)
