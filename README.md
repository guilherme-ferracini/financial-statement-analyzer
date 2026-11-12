# Financial Statement Analyzer

[![tests](https://github.com/guilherme-ferracini/financial-statement-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/guilherme-ferracini/financial-statement-analyzer/actions)

Turns an income statement and a balance sheet into an **executive report**: key metrics, rule-based alerts and a plain-language summary written by an LLM (Claude or OpenAI), ready for a business owner to read.

## Why this exists

At the accounting firm where I lead automation, analysing a client's financial statements used to be a manual, multi-day task: reading the statements, computing ratios in spreadsheets, spotting what changed and writing it up for the client. Automating that cut the turnaround from days to minutes.

This repo is a clean, standalone rewrite of that approach, using fictional data:

- **Code computes, the LLM explains.** Every number (margins, liquidity, leverage, working capital) is calculated in Python and covered by tests. The model only writes the narrative and is instructed not to invent figures. That keeps the output auditable.
- **Explicit rules.** Alerts come from readable thresholds in `flags.py` (e.g. net debt / EBITDA above 2x, revenue up but profit down), so an accountant can review and tune them.
- **Provider-agnostic.** Switch between `anthropic`, `openai` or a `mock` demo mode that runs with no API key.

## Pipeline

```
statements.json ──► ratios.py ──► flags.py ──► report.py ──► report.md
                   (metrics)     (alerts)     (LLM summary)
```

## Quickstart

```bash
pip install -r requirements.txt

# Demo mode: no API key needed
python -m fsa samples/aurora_distribuidora.json --out out/report.md

# Real AI summary
export LLM_PROVIDER=anthropic ANTHROPIC_API_KEY=...   # or LLM_PROVIDER=openai OPENAI_API_KEY=...
python -m fsa samples/aurora_distribuidora.json
```

See [`samples/sample_report.md`](samples/sample_report.md) for the output on the fictional company **Aurora Distribuidora**. Revenue grew 9.5%, but net income fell almost 70%: margins narrowed, interest coverage dropped to 1.4x and the cash conversion cycle grew by 26 days. Those are exactly the signals an accountant wants surfaced before the client meeting.

## Metrics computed

Net revenue, gross profit, EBITDA, EBIT, net income · gross / EBITDA / net margins · current and quick ratios · net debt, net debt / EBITDA, debt / equity · ROE · interest coverage · DSO, DIO, DPO and cash conversion cycle · year-over-year growth.

## Input format

One JSON file with `income_statement` and `balance_sheet` per year. See the sample for the exact fields. In production, a loader maps each client's spreadsheet layout to this format.

## Tests

```bash
python -m pytest -q
```

## Configuration

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | `mock` (default), `anthropic` or `openai` |
| `LLM_MODEL` | override the default model |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | credentials for the chosen provider |

## License

MIT
