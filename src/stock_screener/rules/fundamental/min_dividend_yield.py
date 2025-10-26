"""Rule enforcing a minimum dividend yield requirement."""
from __future__ import annotations

from dataclasses import dataclass

from .. import Rule, RuleResult
from ...models import StockFinancials


@dataclass(frozen=True)
class MinDividendYieldRule:
    """Reject stocks whose dividend yield is below a configured threshold."""

    threshold: float
    name: str = "Min dividend yield"

    def evaluate(self, financials: StockFinancials) -> RuleResult:
        value = financials.dividend_yield
        if value is None:
            return RuleResult(passed=False, reason="Dividend yield data unavailable")
        if value < self.threshold:
            return RuleResult(
                passed=False,
                reason=f"Dividend yield {value:.2f}% below minimum {self.threshold:.2f}%",
            )
        return RuleResult(passed=True)

    def describe(self) -> str:
        return f"Min dividend yield: {self.threshold:.2f}%"


__all__ = ["MinDividendYieldRule"]
