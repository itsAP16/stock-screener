"""Core screening logic."""
from __future__ import annotations

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


def screen_stocks(
    tickers: Iterable[str],
    criteria: StockFilterCriteria,
) -> tuple[list[StockFinancials], list[FetchResult]]:
    """Screen stocks based on the supplied ``criteria``.

    Returns a tuple where the first element is a list of matching ``StockFinancials``
    and the second element contains fetch results for tickers that failed to load.
    """

    matches: list[StockFinancials] = []
    errors: list[FetchResult] = []

    for result in fetch_many(tickers):
        if result.financials is None:
            errors.append(result)
            continue

        if criteria.matches(result.financials):
            matches.append(result.financials)

    return matches, errors
