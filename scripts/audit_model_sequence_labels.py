#!/usr/bin/env python3
"""Audit a model-sequence sample for label leakage risk."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.model_sequence_audit import (
    ModelSequenceAuditError,
    audit_report_markdown,
    label_leakage_audit,
    load_model_sequence_sample,
    write_json,
    write_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit model-sequence labels against feature tokens.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input sample JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = load_model_sequence_sample(args.input_path)
        report = label_leakage_audit(data)
    except ModelSequenceAuditError as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        write_json(args.output_path, report)
    else:
        write_markdown(args.output_path, audit_report_markdown(report))
    print(f"wrote model sequence label audit: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
