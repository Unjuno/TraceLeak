#!/usr/bin/env python3
"""Convert a model sequence NN comparison JSON file into a report.

Usage:
  python scripts/model_sequence_comparison_to_report.py --in comparison.json --out comparison.md
  python scripts/model_sequence_comparison_to_report.py --in comparison.json --out comparison_report.json --format json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.model_sequence_comparison_reporting import (
    ModelSequenceComparisonReportingError,
    load_model_sequence_comparison,
    model_sequence_comparison_report_dict,
    write_model_sequence_comparison_report_json,
    write_model_sequence_comparison_report_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a model sequence comparison into a report.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input comparison JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument(
        "--control",
        dest="control_paths",
        action="append",
        default=[],
        type=Path,
        help="Optional control comparison JSON; may be passed multiple times",
    )
    parser.add_argument(
        "--expected-attribution-token",
        dest="expected_attribution_tokens",
        action="append",
        default=[],
        help="Expected source-level attribution token; may be passed multiple times",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        comparison = load_model_sequence_comparison(args.input_path)
        controls = [load_model_sequence_comparison(path) for path in args.control_paths]
        report = model_sequence_comparison_report_dict(
            comparison,
            controls=controls,
            expected_attribution_tokens=args.expected_attribution_tokens,
        )
    except ModelSequenceComparisonReportingError as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        write_model_sequence_comparison_report_json(args.output_path, report)
    else:
        write_model_sequence_comparison_report_markdown(args.output_path, report)
    print(f"wrote model sequence comparison report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
