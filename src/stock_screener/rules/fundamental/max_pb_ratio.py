"""Rule enforcing a maximum price-to-book (P/B) ratio."""
from __future__ import annotations

from dataclasses import dataclass

from .. import Rule, RuleResult
from ...models import StockFinancials


@dataclass(frozen=True)
class MaxPBRatioRule:
    """Reject stocks whose P/B ratio exceeds a configured threshold."""

    threshold: float
    name: str = "Max P/B ratio"

    def evaluate(self, financials: StockFinancials) -> RuleResult:
        value = financials.pb_ratio
        if value is None:
            return RuleResult(passed=False, reason="P/B ratio data unavailable")
        if value > self.threshold:
            return RuleResult(
                passed=False,
                reason=f"P/B ratio {value:.2f} exceeds limit {self.threshold:.2f}",
            )
        return RuleResult(passed=True)

    def describe(self) -> str:
        return f"Max P/B ratio: {self.threshold:.2f}"


__all__ = ["MaxPBRatioRule"]
