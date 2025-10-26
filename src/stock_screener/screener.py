"""Core screening logic."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .criteria import StockFilterCriteria
from .data import FetchResult, fetch_many
from .models import StockFinancials

DEFAULT_TICKERS: Sequence[str] = (
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "NVDA",
    "JPM",
    "JNJ",
    "V",
)


@dataclass(frozen=True)
class ScreeningResult:
    """Aggregate outcome from screening a batch of tickers."""

    matches: list[StockFinancials]
    non_matches: list[StockFinancials]
    errors: list[FetchResult]


def screen_stocks(
    tickers: Iterable[str],
    criteria: StockFilterCriteria,
) -> ScreeningResult:
    """Screen stocks based on the supplied ``criteria``.

    Returns a ``ScreeningResult`` containing the matching and non-matching
    ``StockFinancials`` as well as any tickers that failed to load.
    """

    matches: list[StockFinancials] = []
    non_matches: list[StockFinancials] = []
    errors: list[FetchResult] = []

    for result in fetch_many(tickers):
        if result.financials is None:
            errors.append(result)
            continue

        if criteria.matches(result.financials):
            matches.append(result.financials)
        else:
            non_matches.append(result.financials)

    return ScreeningResult(matches=matches, non_matches=non_matches, errors=errors)
