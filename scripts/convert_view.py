#!/usr/bin/env python3
"""Convert TraceLeak JSONL files into safer views.

Usage:
  python scripts/convert_view.py --view path --in raw.jsonl --out path.jsonl
  python scripts/convert_view.py --view redacted --in raw.jsonl --out redacted.jsonl
  python scripts/convert_view.py --view meta --in raw.jsonl --out meta.jsonl
"""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.io import read_jsonl, write_jsonl
from traceleak.views import to_view


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert TraceLeak traces to a selected view.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input JSONL file")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output JSONL file")
    parser.add_argument(
        "--view",
        required=True,
        choices=["meta", "path", "redacted"],
        help="Target public-safe view",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output_path.exists() and not args.overwrite:
        raise SystemExit(f"output exists; use --overwrite: {args.output_path}")

    runs = (to_view(run, args.view) for run in read_jsonl(args.input_path))
    write_jsonl(args.output_path, runs)
    print(f"wrote {args.view} view: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
