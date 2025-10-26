"""Filtering criteria used to decide whether a stock passes the screen."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from .models import StockFinancials


@dataclass(frozen=True)
class StockFilterCriteria:
    """Filter configuration for the stock screener."""

    max_pe_ratio: Optional[float] = None
    max_pb_ratio: Optional[float] = None
    min_dividend_yield: Optional[float] = None
    min_market_cap: Optional[float] = None

    def matches(self, financials: "StockFinancials") -> bool:
        """Return ``True`` if the provided financials satisfy all configured filters."""

        return not self.rejection_reasons(financials)

    def rejection_reasons(self, financials: "StockFinancials") -> list[str]:
        """Return human readable explanations for why ``financials`` failed the screen."""

        from .models import StockFinancials  # Local import to avoid circular dependency.

        if not isinstance(financials, StockFinancials):  # defensive guard
            raise TypeError("financials must be a StockFinancials instance")

        reasons: list[str] = []

        self._check_maximum(
            value=financials.pe_ratio,
            threshold=self.max_pe_ratio,
            metric_name="P/E ratio",
            reasons=reasons,
        )
        self._check_maximum(
            value=financials.pb_ratio,
            threshold=self.max_pb_ratio,
            metric_name="P/B ratio",
            reasons=reasons,
        )
        self._check_minimum(
            value=financials.dividend_yield,
            threshold=self.min_dividend_yield,
            metric_name="Dividend yield",
            missing_message="Dividend yield data unavailable",
            reasons=reasons,
        )
        self._check_minimum(
            value=financials.market_cap,
            threshold=self.min_market_cap,
            metric_name="Market capitalization",
            reasons=reasons,
        )

        return reasons

    def describe(self) -> Sequence[str]:
        """Return a list of human-friendly strings summarising the criteria."""

        parts: list[str] = []
        parts.append(
            f"Max P/E ratio: {self.max_pe_ratio:.2f}" if self.max_pe_ratio is not None else "Max P/E ratio: not set"
        )
        parts.append(
            f"Max P/B ratio: {self.max_pb_ratio:.2f}" if self.max_pb_ratio is not None else "Max P/B ratio: not set"
        )
        parts.append(
            "Min dividend yield: "
            + (
                f"{self.min_dividend_yield:.2f}%" if self.min_dividend_yield is not None else "not set"
            )
        )
        parts.append(
            "Min market cap: "
            + (
                f"{self.min_market_cap:,.0f} USD" if self.min_market_cap is not None else "not set"
            )
        )
        return parts

    def _check_maximum(
        self,
        *,
        value: Optional[float],
        threshold: Optional[float],
        metric_name: str,
        reasons: list[str],
        missing_message: str | None = None,
    ) -> None:
        if threshold is None:
            return
        if value is None:
            reasons.append(missing_message or f"{metric_name} data unavailable")
            return
        if value > threshold:
            reasons.append(f"{metric_name} {value:.2f} exceeds limit {threshold:.2f}")

    def _check_minimum(
        self,
        *,
        value: Optional[float],
        threshold: Optional[float],
        metric_name: str,
        reasons: list[str],
        missing_message: str | None = None,
    ) -> None:
        if threshold is None:
            return
        if value is None:
            reasons.append(missing_message or f"{metric_name} data unavailable")
            return
        if value < threshold:
            if metric_name.endswith("yield"):
                reasons.append(f"{metric_name} {value:.2f}% below minimum {threshold:.2f}%")
            else:
                reasons.append(f"{metric_name} {value:,.2f} below minimum {threshold:,.2f}")
