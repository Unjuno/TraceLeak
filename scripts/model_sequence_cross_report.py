#!/usr/bin/env python3
"""Render a cross-target model sequence NN comparison report.

Usage:
  python scripts/model_sequence_cross_report.py \
    --entry synthetic=synthetic_comparison.json \
    --control synthetic=synthetic_control_001.json \
    --entry toy=toy_comparison.json \
    --control toy=toy_control_001.json \
    --out cross_report.md
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from traceleak.model_sequence_cross_report import (
    ModelSequenceCrossReportError,
    model_sequence_cross_report_dict,
    write_model_sequence_cross_report_json,
    write_model_sequence_cross_report_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a model sequence cross report.")
    parser.add_argument(
        "--entry",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Named comparison JSON entry; may be passed multiple times",
    )
    parser.add_argument(
        "--control",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Named control comparison JSON; may be passed multiple times",
    )
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        entries = _load_entries(args.entry, args.control)
        report = model_sequence_cross_report_dict(entries)
    except ModelSequenceCrossReportError as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        write_model_sequence_cross_report_json(args.output_path, report)
    else:
        write_model_sequence_cross_report_markdown(args.output_path, report)
    print(f"wrote model sequence cross report: {args.output_path}")
    return 0


def _load_entries(entry_specs: list[str], control_specs: list[str]) -> list[dict]:
    if not entry_specs:
        raise ModelSequenceCrossReportError("at least one --entry NAME=PATH is required")

    controls_by_name: dict[str, list[dict]] = defaultdict(list)
    for spec in control_specs:
        name, path = _parse_named_path(spec, flag="--control")
        controls_by_name[name].append(_load_json_file(path))

    entries = []
    for spec in entry_specs:
        name, path = _parse_named_path(spec, flag="--entry")
        entries.append(
            {
                "name": name,
                "comparison": _load_json_file(path),
                "controls": controls_by_name.get(name, []),
            }
        )
    return entries


def _parse_named_path(spec: str, *, flag: str) -> tuple[str, Path]:
    if "=" not in spec:
        raise ModelSequenceCrossReportError(f"{flag} must use NAME=PATH format: {spec}")
    name, raw_path = spec.split("=", 1)
    name = name.strip()
    if not name:
        raise ModelSequenceCrossReportError(f"{flag} name must not be empty")
    path = Path(raw_path.strip())
    if not path.exists():
        raise ModelSequenceCrossReportError(f"input file not found: {path}")
    return name, path


def _load_json_file(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelSequenceCrossReportError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ModelSequenceCrossReportError(f"input must be a JSON object: {path}")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
