#!/usr/bin/env python3
"""Render a TraceLeak comparison file as Markdown or JSON.

Usage:
  python scripts/comparison_to_report.py --in examples/synthetic/comparison_sample.json --out comparison_report.md
  python scripts/comparison_to_report.py --in examples/synthetic/comparison_sample.json --out comparison_report.json --format json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.comparison import (
    ComparisonError,
    comparison_report_dict,
    load_comparison,
    write_comparison_report_json,
    write_comparison_report_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a TraceLeak public-safe comparison report.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input comparison JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--allow-raw", action="store_true", help="Allow non-public-safe views")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = load_comparison(args.input_path)
        report = comparison_report_dict(data, public_safe=not args.allow_raw)
    except ComparisonError as exc:
        raise SystemExit(f"error: {exc}") from exc

    if args.format == "json":
        write_comparison_report_json(args.output_path, report)
    else:
        write_comparison_report_markdown(args.output_path, report)
    print(f"wrote comparison report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
