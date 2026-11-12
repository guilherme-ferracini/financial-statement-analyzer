"""Rule-based alerts. Thresholds are explicit and easy to tune per client segment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .ratios import YearMetrics, growth


@dataclass
class Flag:
    severity: str   # "high" | "medium" | "info"
    area: str
    message: str


def _pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x * 100:.1f}%"


def evaluate(cur: YearMetrics, prev: Optional[YearMetrics] = None) -> List[Flag]:
    flags: List[Flag] = []

    if cur.current_ratio is not None and cur.current_ratio < 1.0:
        flags.append(Flag("high", "liquidity",
                          f"Current ratio at {cur.current_ratio:.2f}: short-term liabilities exceed current assets."))
    elif cur.current_ratio is not None and cur.current_ratio < 1.2:
        flags.append(Flag("medium", "liquidity", f"Current ratio is tight at {cur.current_ratio:.2f}."))

    if cur.net_debt_to_ebitda is not None and cur.net_debt_to_ebitda > 3:
        flags.append(Flag("high", "leverage", f"Net debt / EBITDA at {cur.net_debt_to_ebitda:.1f}x (above 3x)."))
    elif cur.net_debt_to_ebitda is not None and cur.net_debt_to_ebitda > 2:
        flags.append(Flag("medium", "leverage", f"Net debt / EBITDA at {cur.net_debt_to_ebitda:.1f}x (above 2x)."))

    if cur.interest_coverage is not None and cur.interest_coverage < 2:
        flags.append(Flag("high", "leverage",
                          f"EBIT covers financial expenses only {cur.interest_coverage:.1f}x."))

    if cur.net_income < 0:
        flags.append(Flag("high", "profitability", "The company posted a net loss."))

    if prev is not None:
        rev_g = growth(cur.net_revenue, prev.net_revenue)
        ni_g = growth(cur.net_income, prev.net_income)
        if rev_g is not None:
            flags.append(Flag("info", "growth", f"Net revenue grew {_pct(rev_g)} year over year."))
        if rev_g is not None and ni_g is not None and rev_g > 0 and ni_g < 0:
            flags.append(Flag("high", "profitability",
                              f"Revenue grew {_pct(rev_g)} but net income fell {_pct(-ni_g)}: growth is not reaching the bottom line."))
        if cur.gross_margin is not None and prev.gross_margin is not None:
            delta = cur.gross_margin - prev.gross_margin
            if delta < -0.02:
                flags.append(Flag("medium", "profitability",
                                  f"Gross margin dropped {abs(delta) * 100:.1f} p.p. to {_pct(cur.gross_margin)}."))
        if cur.cash_conversion_cycle is not None and prev.cash_conversion_cycle is not None:
            delta_days = cur.cash_conversion_cycle - prev.cash_conversion_cycle
            if delta_days > 10:
                flags.append(Flag("medium", "working capital",
                                  f"Cash conversion cycle lengthened by {delta_days:.0f} days to {cur.cash_conversion_cycle:.0f} days."))

    order = {"high": 0, "medium": 1, "info": 2}
    return sorted(flags, key=lambda f: order[f.severity])
