"""Caching utilities for data retrieval."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from threading import RLock

from .base import FetchResult


class DataCache(ABC):
    """Interface for caching :class:`FetchResult` objects."""

    @abstractmethod
    def get(self, ticker: str) -> FetchResult | None:
        """Return the cached result for ``ticker`` if available."""

    @abstractmethod
    def set(self, result: FetchResult) -> None:
        """Store ``result`` in the cache."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all cached entries."""


class InMemoryCache(DataCache):
    """Thread-safe in-memory cache for ``FetchResult`` objects."""

    def __init__(self, store: MutableMapping[str, FetchResult] | None = None) -> None:
        self._store: MutableMapping[str, FetchResult] = store or {}
        self._lock = RLock()

    def get(self, ticker: str) -> FetchResult | None:
        key = ticker.upper()
        with self._lock:
            return self._store.get(key)

    def set(self, result: FetchResult) -> None:
        key = result.ticker.upper()
        with self._lock:
            self._store[key] = result

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
