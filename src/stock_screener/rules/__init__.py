"""Reusable screening rules for the stock screener."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from ..models import StockFinancials


@dataclass(frozen=True)
class RuleResult:
    """Outcome of applying a screening rule."""

    passed: bool
    reason: str | None = None


class Rule(Protocol):
    """Common interface implemented by all screening rules."""

    name: str

    def evaluate(self, financials: "StockFinancials") -> RuleResult:
        """Return the outcome of applying the rule to ``financials``."""

    def describe(self) -> str:
        """Return a human friendly description of the rule configuration."""


__all__ = ["Rule", "RuleResult"]
