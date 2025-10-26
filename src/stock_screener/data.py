"""Data access layer for retrieving metrics from Yahoo Finance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

import yfinance as yf

from .models import StockFinancials


@dataclass(frozen=True)
class FetchResult:
    """Result returned when attempting to fetch data for a ticker."""

    ticker: str
    financials: StockFinancials | None
    error: str | None = None


def fetch_financials(ticker: str) -> FetchResult:
    """Retrieve valuation metrics for a single ticker.

    Parameters
    ----------
    ticker:
        The ticker symbol to fetch.

    Returns
    -------
    FetchResult
        An object containing the retrieved ``StockFinancials`` or an error message.
    """

    ticker_obj = yf.Ticker(ticker)
    try:
        info = ticker_obj.info
    except Exception as exc:  # pragma: no cover - defensive programming
        return FetchResult(ticker=ticker.upper(), financials=None, error=str(exc))

    financials = StockFinancials(
        ticker=ticker.upper(),
        pe_ratio=_safe_float(info, "trailingPE"),
        pb_ratio=_safe_float(info, "priceToBook"),
        dividend_yield=_safe_percentage(info, "dividendYield"),
        market_cap=_safe_float(info, "marketCap"),
    )

    return FetchResult(ticker=ticker.upper(), financials=financials)


def fetch_many(tickers: Iterable[str]) -> Iterator[FetchResult]:
    """Yield ``FetchResult`` objects for each ticker provided."""

    for ticker in tickers:
        yield fetch_financials(ticker)


def _safe_float(info: dict, key: str) -> float | None:
    value = info.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive programming
        return None


def _safe_percentage(info: dict, key: str) -> float | None:
    value = _safe_float(info, key)
    if value is None:
        return None
    return value * 100
