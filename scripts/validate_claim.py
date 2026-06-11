#!/usr/bin/env python3
"""Validate TraceLeak claim level JSON files.

Usage:
  python scripts/validate_claim.py examples/synthetic/claim_l5_sample.json
  python scripts/validate_claim.py --json examples/synthetic/claim_l5_sample.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.claim_levels import ClaimLevelError, claim_summary, load_claim, validate_claim


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate TraceLeak claim level files.")
    parser.add_argument("paths", nargs="+", type=Path, help="Claim JSON files")
    parser.add_argument("--allow-raw", action="store_true", help="Allow non-public-safe claim views")
    parser.add_argument("--json", action="store_true", help="Print JSON summaries")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failed = 0
    summaries = []
    for path in args.paths:
        try:
            claim = load_claim(path)
            validate_claim(claim, public_safe=not args.allow_raw)
        except ClaimLevelError as exc:
            failed += 1
            print(f"{path}: invalid: {exc}")
            continue
        summary = claim_summary(claim)
        summaries.append(summary)
        if not args.json:
            print(f"{path}: ok ({summary['claim_id']}, {summary['level']})")

    if args.json:
        print(json.dumps(summaries, indent=2, sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
