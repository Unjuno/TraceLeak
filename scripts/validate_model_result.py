#!/usr/bin/env python3
"""Validate TraceLeak model result JSON files.

Usage:
  python scripts/validate_model_result.py examples/synthetic/model_result_sample.json
  python scripts/validate_model_result.py --json examples/synthetic/model_result_sample.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.model_results import (
    ModelResultError,
    load_model_result,
    model_result_summary,
    validate_model_result,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate TraceLeak model result files.")
    parser.add_argument("paths", nargs="+", type=Path, help="Model result JSON files")
    parser.add_argument("--allow-raw", action="store_true", help="Allow non-public-safe views")
    parser.add_argument("--json", action="store_true", help="Print JSON summaries")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failed = 0
    summaries = []
    for path in args.paths:
        try:
            result = load_model_result(path)
            validate_model_result(result, public_safe=not args.allow_raw)
        except ModelResultError as exc:
            failed += 1
            print(f"{path}: invalid: {exc}")
            continue
        summary = model_result_summary(result)
        summaries.append(summary)
        if not args.json:
            print(f"{path}: ok ({summary['experiment_id']}, {summary['model_type']})")

    if args.json:
        print(json.dumps(summaries, indent=2, sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
