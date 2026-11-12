"""python -m fsa samples/aurora_distribuidora.json [--provider mock|anthropic|openai] [--out report.md]"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .llm import LLMClient
from .report import build_report, mock_summary


def main() -> None:
    p = argparse.ArgumentParser(description="AI-assisted financial statement analysis")
    p.add_argument("statements", type=Path, help="JSON file with income statement and balance sheet by year")
    p.add_argument("--provider", default=None, help="mock (default), anthropic or openai")
    p.add_argument("--model", default=None)
    p.add_argument("--out", type=Path, default=None, help="write the Markdown report to this file")
    a = p.parse_args()

    statements = json.loads(a.statements.read_text(encoding="utf-8"))
    client = LLMClient(a.provider, a.model, mock_fn=mock_summary)
    report = build_report(statements, client)

    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(report, encoding="utf-8")
        print(f"Report written to {a.out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
