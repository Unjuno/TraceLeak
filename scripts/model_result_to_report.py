#!/usr/bin/env python3
"""Convert a TraceLeak model result JSON file into a report.

Usage:
  python scripts/model_result_to_report.py --in examples/synthetic/model_result_sample.json --out report.md
  python scripts/model_result_to_report.py --in examples/synthetic/model_result_sample.json --out report.json --format json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.model_reporting import ModelReportingError, model_result_to_report
from traceleak.model_results import ModelResultError, load_model_result
from traceleak.reporting import write_report_json, write_report_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a TraceLeak model result into a report.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input model result JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--split", default="test", help="Metric split to report")
    parser.add_argument("--metric", default="DeltaH", help="Metric to report")
    parser.add_argument("--allow-raw", action="store_true", help="Allow non-public-safe views")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = load_model_result(args.input_path)
        report = model_result_to_report(
            result,
            split=args.split,
            metric=args.metric,
            public_safe=not args.allow_raw,
        )
    except (ModelResultError, ModelReportingError) as exc:
        raise SystemExit(f"error: {exc}") from exc

    if args.format == "json":
        write_report_json(args.output_path, report)
    else:
        write_report_markdown(args.output_path, report)
    print(f"wrote model report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
