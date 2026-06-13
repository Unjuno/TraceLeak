#!/usr/bin/env python3
"""Build the P3-P5 review chain summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.review_chain_snapshot import build_review_chain_snapshot
from traceleak.review_chain_summary import build_review_chain_summary, validate_review_chain_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the P3-P5 review chain summary.")
    parser.add_argument("--out", required=True, type=Path, help="Output JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_review_chain_summary(snapshot=build_review_chain_snapshot())
    validate_review_chain_summary(summary)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote review chain summary: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
