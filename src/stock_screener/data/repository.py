"""Repository orchestrating data access and caching."""
from __future__ import annotations

from typing import Iterable, Iterator

from .base import DataSource, FetchResult
from .cache import DataCache


class DataRepository:
    """Coordinate data retrieval, transformation, and caching."""

    def __init__(self, source: DataSource, cache: DataCache | None = None) -> None:
        self._source = source
        self._cache = cache

    def fetch(self, ticker: str, *, use_cache: bool = True) -> FetchResult:
        ticker = ticker.upper()
        if use_cache and self._cache is not None:
            cached = self._cache.get(ticker)
            if cached is not None:
                return cached

        result = self._source.fetch(ticker)

        if self._cache is not None and result.financials is not None:
            self._cache.set(result)

        return result

    def fetch_many(self, tickers: Iterable[str], *, use_cache: bool = True) -> Iterator[FetchResult]:
        for ticker in tickers:
            yield self.fetch(ticker, use_cache=use_cache)
