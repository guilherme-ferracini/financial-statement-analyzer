"""Deterministic financial ratios. The LLM never computes numbers: code does."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


def _div(a: float, b: float) -> Optional[float]:
    return None if not b else a / b


@dataclass
class YearMetrics:
    year: str
    net_revenue: float
    gross_profit: float
    ebitda: float
    ebit: float
    net_income: float
    gross_margin: Optional[float]
    ebitda_margin: Optional[float]
    net_margin: Optional[float]
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    net_debt: float
    net_debt_to_ebitda: Optional[float]
    debt_to_equity: Optional[float]
    roe: Optional[float]
    dso_days: Optional[float]
    dio_days: Optional[float]
    dpo_days: Optional[float]
    cash_conversion_cycle: Optional[float]
    interest_coverage: Optional[float]


def compute_year(year: str, data: Dict) -> YearMetrics:
    i, b = data["income_statement"], data["balance_sheet"]

    net_revenue = i["gross_revenue"] - i["deductions"]
    gross_profit = net_revenue - i["cost_of_goods_sold"]
    ebitda = gross_profit - i["selling_expenses"] - i["administrative_expenses"]
    ebit = ebitda - i["depreciation_amortization"]
    pre_tax = ebit + i["financial_income"] - i["financial_expenses"]
    net_income = pre_tax - i["income_tax"]

    current_assets = b["cash"] + b["accounts_receivable"] + b["inventory"] + b["other_current_assets"]
    current_liabilities = b["accounts_payable"] + b["short_term_debt"] + b["other_current_liabilities"]
    gross_debt = b["short_term_debt"] + b["long_term_debt"]
    net_debt = gross_debt - b["cash"]

    dso = _div(b["accounts_receivable"], net_revenue)
    dio = _div(b["inventory"], i["cost_of_goods_sold"])
    dpo = _div(b["accounts_payable"], i["cost_of_goods_sold"])
    to_days = lambda x: None if x is None else x * 365  # noqa: E731
    ccc = None if None in (dso, dio, dpo) else (dso + dio - dpo) * 365

    return YearMetrics(
        year=year,
        net_revenue=net_revenue,
        gross_profit=gross_profit,
        ebitda=ebitda,
        ebit=ebit,
        net_income=net_income,
        gross_margin=_div(gross_profit, net_revenue),
        ebitda_margin=_div(ebitda, net_revenue),
        net_margin=_div(net_income, net_revenue),
        current_ratio=_div(current_assets, current_liabilities),
        quick_ratio=_div(current_assets - b["inventory"], current_liabilities),
        net_debt=net_debt,
        net_debt_to_ebitda=_div(net_debt, ebitda),
        debt_to_equity=_div(gross_debt, b["equity"]),
        roe=_div(net_income, b["equity"]),
        dso_days=to_days(dso),
        dio_days=to_days(dio),
        dpo_days=to_days(dpo),
        cash_conversion_cycle=ccc,
        interest_coverage=_div(ebit, i["financial_expenses"]),
    )


def growth(current: float, previous: float) -> Optional[float]:
    return None if not previous else current / previous - 1
