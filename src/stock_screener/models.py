"""Data models used by the stock screener."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence


@dataclass(frozen=True)
class StockFinancials:
    """Snapshot of a company's key valuation metrics.

    The ``price_history`` attribute can be used to store a sequence of
    ``(date, price)`` pairs—such as daily closing prices—to enable
    time-series analysis alongside the point-in-time metrics.
    """

    ticker: str
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    dividend_yield: Optional[float]
    market_cap: Optional[float]
    price_history: Optional[Sequence[tuple[date, float]]] = None

    def metadata(self) -> list[Optional[float] | str]:
        """Return only the point-in-time metrics for tabular display."""

        return [
            self.ticker,
            self.pe_ratio,
            self.pb_ratio,
            self.dividend_yield,
            self.market_cap,
        ]

    @classmethod
    def builder(cls, ticker: str) -> StockFinancialsBuilder:
        """Start a builder for ``StockFinancials`` instances."""

        return StockFinancialsBuilder(ticker=ticker)


class StockFinancialsBuilder:
    """Builder for :class:`StockFinancials`."""

    def __init__(
        self,
        *,
        ticker: str,
        pe_ratio: Optional[float] = None,
        pb_ratio: Optional[float] = None,
        dividend_yield: Optional[float] = None,
        market_cap: Optional[float] = None,
        price_history: Optional[Sequence[tuple[date, float]]] = None,
    ) -> None:
        self._ticker = ticker
        self._pe_ratio = pe_ratio
        self._pb_ratio = pb_ratio
        self._dividend_yield = dividend_yield
        self._market_cap = market_cap
        self._price_history = price_history

    def with_pe_ratio(self, value: Optional[float]) -> StockFinancialsBuilder:
        self._pe_ratio = value
        return self

    def with_pb_ratio(self, value: Optional[float]) -> StockFinancialsBuilder:
        self._pb_ratio = value
        return self

    def with_dividend_yield(self, value: Optional[float]) -> StockFinancialsBuilder:
        self._dividend_yield = value
        return self

    def with_market_cap(self, value: Optional[float]) -> StockFinancialsBuilder:
        self._market_cap = value
        return self

    def with_price_history(
        self, value: Optional[Sequence[tuple[date, float]]]
    ) -> StockFinancialsBuilder:
        self._price_history = value
        return self

    def build(self) -> StockFinancials:
        return StockFinancials(
            ticker=self._ticker,
            pe_ratio=self._pe_ratio,
            pb_ratio=self._pb_ratio,
            dividend_yield=self._dividend_yield,
            market_cap=self._market_cap,
            price_history=self._price_history,
        )
