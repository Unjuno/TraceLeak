#!/usr/bin/env python3
"""Evaluate repeated-run TraceLeak stability inputs.

Usage:
  python scripts/evaluate_stability.py examples/synthetic/stability_sample.json
  python scripts/evaluate_stability.py --out stability_result.json examples/synthetic/stability_sample.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.stability import StabilityError, load_stability_input, stability_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate repeated-run TraceLeak stability inputs.")
    parser.add_argument("input_path", type=Path, help="Input stability JSON")
    parser.add_argument("--out", dest="output_path", type=Path, help="Optional JSON output path")
    parser.add_argument("--allow-raw", action="store_true", help="Allow non-public-safe views")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = load_stability_input(args.input_path)
        result = stability_result(data, public_safe=not args.allow_raw)
    except StabilityError as exc:
        raise SystemExit(f"error: {exc}") from exc

    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output_path:
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(payload + "\n", encoding="utf-8")
        print(f"wrote stability result: {args.output_path}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
