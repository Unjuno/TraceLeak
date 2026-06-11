#!/usr/bin/env python3
"""Render a TraceLeak patch verification file as Markdown or JSON.

Usage:
  python scripts/patch_verification_to_report.py --in examples/synthetic/patch_verification_sample.json --out patch_report.md
  python scripts/patch_verification_to_report.py --in examples/synthetic/patch_verification_sample.json --out patch_report.json --format json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.patch_reporting import (
    patch_verification_report_dict,
    write_patch_verification_report_json,
    write_patch_verification_report_markdown,
)
from traceleak.patch_verification import (
    PatchVerificationError,
    load_patch_verification,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a TraceLeak patch verification report.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input verification JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--allow-raw", action="store_true", help="Allow non-public-safe views")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = load_patch_verification(args.input_path)
        report = patch_verification_report_dict(result, public_safe=not args.allow_raw)
    except PatchVerificationError as exc:
        raise SystemExit(f"error: {exc}") from exc

    if args.format == "json":
        write_patch_verification_report_json(args.output_path, report)
    else:
        write_patch_verification_report_markdown(args.output_path, report)
    print(f"wrote patch verification report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
