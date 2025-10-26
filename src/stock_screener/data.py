"""Data access layer for retrieving metrics from Yahoo Finance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, TYPE_CHECKING

try:  # pragma: no cover - import guard
    import yfinance as yf
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yf = None  # type: ignore[assignment]
    _YFINANCE_IMPORT_ERROR = (
        "The 'yfinance' package is required to fetch stock data. "
        "Install it with `pip install yfinance`."
    )
else:
    _YFINANCE_IMPORT_ERROR = ""

if TYPE_CHECKING:  # pragma: no cover - typing only
    import yfinance as _yfinance

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

    ticker_obj = _require_yfinance().Ticker(ticker)
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


def _require_yfinance() -> "_yfinance":
    if yf is None:
        raise ModuleNotFoundError(_YFINANCE_IMPORT_ERROR)
    return yf


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
