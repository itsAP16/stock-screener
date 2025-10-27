"""Yahoo Finance implementation of the :class:`DataSource` interface."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import DataSource, FetchResult
from ..models import StockFinancials

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


class YahooFinanceDataSource(DataSource):
    """Retrieve stock data from Yahoo Finance."""

    def __init__(self, client: "_yfinance" | None = None) -> None:
        self._client = client or _require_yfinance()

    def fetch(self, ticker: str) -> FetchResult:
        ticker = ticker.upper()
        ticker_obj = self._client.Ticker(ticker)
        try:
            info = ticker_obj.info
        except Exception as exc:  # pragma: no cover - defensive programming
            return FetchResult(ticker=ticker, financials=None, error=str(exc))

        financials = StockFinancials(
            ticker=ticker,
            pe_ratio=_safe_float(info, "trailingPE"),
            pb_ratio=_safe_float(info, "priceToBook"),
            dividend_yield=_safe_percentage(info, "dividendYield"),
            market_cap=_safe_float(info, "marketCap"),
        )

        return FetchResult(ticker=ticker, financials=financials)


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
