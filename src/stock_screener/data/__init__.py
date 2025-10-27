"""Modular data access layer supporting multiple data sources."""
from __future__ import annotations

from typing import Iterable, Iterator

from .base import DataSource, FetchResult
from .cache import DataCache, InMemoryCache
from .repository import DataRepository
from .yahoo import YahooFinanceDataSource

__all__ = [
    "DataSource",
    "FetchResult",
    "DataCache",
    "InMemoryCache",
    "DataRepository",
    "YahooFinanceDataSource",
    "get_default_repository",
    "fetch_financials",
    "fetch_many",
]


_default_repository: DataRepository | None = None


def get_default_repository() -> DataRepository:
    """Return the lazily-instantiated default :class:`DataRepository`."""

    global _default_repository
    if _default_repository is None:
        _default_repository = DataRepository(
            YahooFinanceDataSource(),
            cache=InMemoryCache(),
        )
    return _default_repository


def fetch_financials(ticker: str) -> FetchResult:
    """Convenience wrapper around ``get_default_repository().fetch``."""

    return get_default_repository().fetch(ticker)


def fetch_many(tickers: Iterable[str]) -> Iterator[FetchResult]:
    """Convenience wrapper around ``get_default_repository().fetch_many``."""

    return get_default_repository().fetch_many(tickers)
