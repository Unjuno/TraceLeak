#!/usr/bin/env python3
"""Validate TraceLeak patch verification JSON files.

Usage:
  python scripts/validate_patch_verification.py examples/synthetic/patch_verification_sample.json
  python scripts/validate_patch_verification.py --json examples/synthetic/patch_verification_sample.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.patch_verification import (
    PatchVerificationError,
    load_patch_verification,
    patch_verification_summary,
    validate_patch_verification,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate TraceLeak patch verification files.")
    parser.add_argument("paths", nargs="+", type=Path, help="Patch verification JSON files")
    parser.add_argument("--allow-raw", action="store_true", help="Allow non-public-safe views")
    parser.add_argument("--json", action="store_true", help="Print JSON summaries")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failed = 0
    summaries = []
    for path in args.paths:
        try:
            result = load_patch_verification(path)
            validate_patch_verification(result, public_safe=not args.allow_raw)
        except PatchVerificationError as exc:
            failed += 1
            print(f"{path}: invalid: {exc}")
            continue
        summary = patch_verification_summary(result)
        summaries.append(summary)
        if not args.json:
            print(f"{path}: ok ({summary['verification_id']}, {summary['status']})")

    if args.json:
        print(json.dumps(summaries, indent=2, sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
