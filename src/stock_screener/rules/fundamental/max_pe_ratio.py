"""Rule enforcing a maximum price-to-earnings (P/E) ratio."""
from __future__ import annotations

from dataclasses import dataclass

from .. import Rule, RuleResult
from ...models import StockFinancials


@dataclass(frozen=True)
class MaxPERatioRule:
    """Reject stocks whose trailing P/E exceeds a configured threshold."""

    threshold: float
    name: str = "Max P/E ratio"

    def evaluate(self, financials: StockFinancials) -> RuleResult:
        value = financials.pe_ratio
        if value is None:
            return RuleResult(passed=False, reason="P/E ratio data unavailable")
        if value > self.threshold:
            return RuleResult(
                passed=False,
                reason=f"P/E ratio {value:.2f} exceeds limit {self.threshold:.2f}",
            )
        return RuleResult(passed=True)

    def describe(self) -> str:
        return f"Max P/E ratio: {self.threshold:.2f}"


__all__ = ["MaxPERatioRule"]
