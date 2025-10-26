"""Rule enforcing a minimum market capitalisation."""
from __future__ import annotations

from dataclasses import dataclass

from .. import Rule, RuleResult
from ...models import StockFinancials


@dataclass(frozen=True)
class MinMarketCapRule:
    """Reject stocks whose market capitalisation is below a threshold."""

    threshold: float
    name: str = "Min market cap"

    def evaluate(self, financials: StockFinancials) -> RuleResult:
        value = financials.market_cap
        if value is None:
            return RuleResult(passed=False, reason="Market capitalization data unavailable")
        if value < self.threshold:
            return RuleResult(
                passed=False,
                reason=f"Market capitalization {value:,.2f} below minimum {self.threshold:,.2f}",
            )
        return RuleResult(passed=True)

    def describe(self) -> str:
        return f"Min market cap: {self.threshold:,.0f} USD"


__all__ = ["MinMarketCapRule"]
