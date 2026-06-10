#!/usr/bin/env python3
"""Validate TraceLeak JSONL trace files.

This script is intentionally lightweight. It validates schema and, optionally,
public-export safety rules. It does not train models or run OpenSSL.

Usage:
  python scripts/validate_trace.py examples/synthetic/synthetic_trace_sample.jsonl
  python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from traceleak.schema import TraceSchemaError, validate_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate TraceLeak JSONL trace files.")
    parser.add_argument("paths", nargs="+", type=Path, help="JSONL trace files to validate")
    parser.add_argument(
        "--public",
        action="store_true",
        help="enforce public-export safety rules, rejecting raw/cheat traces and raw fields",
    )
    return parser.parse_args()


def validate_path(path: Path, *, public_export: bool) -> tuple[int, int]:
    checked = 0
    failed = 0

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            checked += 1
            try:
                run: dict[str, Any] = json.loads(stripped)
                validate_run(run, public_export=public_export)
            except (json.JSONDecodeError, TraceSchemaError) as exc:
                failed += 1
                print(f"{path}:{line_number}: invalid: {exc}", file=sys.stderr)

    return checked, failed


def main() -> int:
    args = parse_args()
    total_checked = 0
    total_failed = 0

    for path in args.paths:
        if not path.exists():
            print(f"{path}: missing file", file=sys.stderr)
            total_failed += 1
            continue
        checked, failed = validate_path(path, public_export=args.public)
        total_checked += checked
        total_failed += failed
        status = "ok" if failed == 0 else "failed"
        print(f"{path}: {status} ({checked} run(s), {failed} error(s))")

    if total_checked == 0:
        print("no trace runs found", file=sys.stderr)
        return 1
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
