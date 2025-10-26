"""Filtering criteria composed of reusable screening rules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from .models import StockFinancials
from .rules import Rule
from .rules.fundamental import (
    MaxPERatioRule,
    MaxPBRatioRule,
    MinDividendYieldRule,
    MinMarketCapRule,
)


@dataclass(frozen=True, init=False)
class StockFilterCriteria:
    """A collection of reusable screening rules."""

    rules: tuple[Rule, ...]
    _inactive_descriptions: tuple[str, ...]

    def __init__(
        self,
        *,
        rules: Iterable[Rule] | None = None,
        max_pe_ratio: Optional[float] = None,
        max_pb_ratio: Optional[float] = None,
        min_dividend_yield: Optional[float] = None,
        min_market_cap: Optional[float] = None,
    ) -> None:
        configured_rules = list(rules or [])
        inactive_descriptions: list[str] = []
        include_default_descriptions = rules is None

        if max_pe_ratio is not None:
            configured_rules.append(MaxPERatioRule(threshold=max_pe_ratio))
        elif include_default_descriptions:
            inactive_descriptions.append("Max P/E ratio: not set")

        if max_pb_ratio is not None:
            configured_rules.append(MaxPBRatioRule(threshold=max_pb_ratio))
        elif include_default_descriptions:
            inactive_descriptions.append("Max P/B ratio: not set")

        if min_dividend_yield is not None:
            configured_rules.append(MinDividendYieldRule(threshold=min_dividend_yield))
        elif include_default_descriptions:
            inactive_descriptions.append("Min dividend yield: not set")

        if min_market_cap is not None:
            configured_rules.append(MinMarketCapRule(threshold=min_market_cap))
        elif include_default_descriptions:
            inactive_descriptions.append("Min market cap: not set")

        object.__setattr__(self, "rules", tuple(configured_rules))
        object.__setattr__(self, "_inactive_descriptions", tuple(inactive_descriptions))

    def matches(self, financials: StockFinancials) -> bool:
        """Return ``True`` if all configured rules pass for ``financials``."""

        return not self.rejection_reasons(financials)

    def rejection_reasons(self, financials: StockFinancials) -> list[str]:
        """Return human readable explanations for rule failures."""

        if not isinstance(financials, StockFinancials):  # defensive guard
            raise TypeError("financials must be a StockFinancials instance")

        reasons: list[str] = []
        for rule in self.rules:
            result = rule.evaluate(financials)
            if not result.passed:
                reason = result.reason or f"{rule.name} failed"
                reasons.append(reason)
        return reasons

    def describe(self) -> Sequence[str]:
        """Return a list of human-friendly strings summarising the criteria."""

        descriptions = [rule.describe() for rule in self.rules]
        descriptions.extend(self._inactive_descriptions)
        if not descriptions:
            descriptions.append("No screening rules configured.")
        return descriptions


__all__ = ["StockFilterCriteria"]
