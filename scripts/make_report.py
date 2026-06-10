#!/usr/bin/env python3
"""Create a lightweight TraceLeak attribution report from ablation scores.

Input JSON format:
{
  "target": "synthetic-example",
  "view": "redacted",
  "metric": "DeltaH",
  "full_score": 10.0,
  "groups": {
    "branch_event": {
      "ablated_score": 4.0,
      "group_type": "branch",
      "location": "target.c:21"
    }
  },
  "notes": ["optional note"]
}

Usage:
  python scripts/make_report.py --in examples/synthetic/ablation_sample.json --out report.md
  python scripts/make_report.py --in examples/synthetic/ablation_sample.json --out report.json --format json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from traceleak.attribution import make_ablation_scores
from traceleak.reporting import (
    attribution_report_dict,
    write_report_json,
    write_report_markdown,
)


class ReportInputError(ValueError):
    """Raised when an attribution report input is invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a TraceLeak attribution report.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input ablation JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--top", type=int, default=10, help="Number of rows for Markdown output")
    return parser.parse_args()


def load_input(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ReportInputError(
            f"input file not found: {path}\n"
            "Use the sample input:\n"
            "  python scripts/make_report.py --in examples/synthetic/ablation_sample.json --out report.md"
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReportInputError(f"invalid JSON in {path}: {exc}") from exc


def build_report(data: dict[str, Any]) -> dict[str, Any]:
    for key in ("target", "view", "full_score", "groups"):
        if key not in data:
            raise ReportInputError(f"missing required input field: {key}")

    groups = data.get("groups") or {}
    if not isinstance(groups, dict) or not groups:
        raise ReportInputError("groups must be a non-empty object")

    ablated_scores = {}
    locations = {}
    group_types = set()
    for group_id, group_data in groups.items():
        if not isinstance(group_data, dict):
            raise ReportInputError(f"group {group_id!r} must be an object")
        if "ablated_score" not in group_data:
            raise ReportInputError(f"group {group_id!r} is missing ablated_score")
        ablated_scores[group_id] = float(group_data["ablated_score"])
        group_types.add(group_data.get("group_type", "unknown"))
        if "location" in group_data:
            locations[group_id] = group_data["location"]

    group_type = next(iter(group_types)) if len(group_types) == 1 else "mixed"

    attributions = make_ablation_scores(
        full_score=float(data["full_score"]),
        ablated_scores=ablated_scores,
        group_type=group_type,
        locations=locations,
    )
    return attribution_report_dict(
        target=data["target"],
        view=data["view"],
        metric=data.get("metric", "DeltaH"),
        score=float(data["full_score"]),
        attributions=attributions,
        notes=data.get("notes", []),
    )


def main() -> int:
    args = parse_args()
    try:
        report = build_report(load_input(args.input_path))
    except ReportInputError as exc:
        raise SystemExit(f"error: {exc}") from exc

    if args.format == "json":
        write_report_json(args.output_path, report)
    else:
        write_report_markdown(args.output_path, report, top_n=args.top)
    print(f"wrote report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
