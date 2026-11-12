import json
from pathlib import Path

import pytest

from fsa.flags import evaluate
from fsa.llm import LLMClient
from fsa.ratios import compute_year
from fsa.report import analyse, build_report, mock_summary

SAMPLE = json.loads((Path(__file__).parents[1] / "samples" / "aurora_distribuidora.json").read_text())


def test_income_statement_math():
    m = compute_year("2025", SAMPLE["years"]["2025"])
    assert m.net_revenue == 20150000 - 3020000
    assert m.gross_profit == m.net_revenue - 12480000
    assert m.ebitda == m.gross_profit - 1690000 - 1340000
    assert m.net_income == m.ebitda - 335000 + 70000 - 910000 - 205000


def test_ratios():
    m = compute_year("2025", SAMPLE["years"]["2025"])
    assert m.current_ratio == pytest.approx((640000 + 3310000 + 3720000 + 230000) / (2050000 + 2380000 + 760000))
    assert m.net_debt == 2380000 + 1960000 - 640000
    assert m.dso_days == pytest.approx(3310000 / m.net_revenue * 365)


def test_flags_catch_profit_squeeze():
    metrics, flags = analyse(SAMPLE)
    messages = " ".join(f.message for f in flags)
    assert "not reaching the bottom line" in messages
    assert flags[0].severity == "high"


def test_healthy_company_has_no_high_flags():
    healthy = {
        "income_statement": {
            "gross_revenue": 1000, "deductions": 100, "cost_of_goods_sold": 400,
            "selling_expenses": 100, "administrative_expenses": 100, "depreciation_amortization": 20,
            "financial_income": 10, "financial_expenses": 10, "income_tax": 50,
        },
        "balance_sheet": {
            "cash": 500, "accounts_receivable": 100, "inventory": 100, "other_current_assets": 0,
            "non_current_assets": 300, "accounts_payable": 100, "short_term_debt": 50,
            "other_current_liabilities": 50, "long_term_debt": 100, "equity": 700,
        },
    }
    flags = evaluate(compute_year("2025", healthy))
    assert not [f for f in flags if f.severity == "high"]


def test_report_in_demo_mode():
    report = build_report(SAMPLE, LLMClient("mock", mock_fn=mock_summary))
    assert "## Key metrics" in report
    assert "## Executive summary" in report
    assert "Demo mode" in report
