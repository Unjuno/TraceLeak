#!/usr/bin/env python3
"""Build a path-based DeepProgramSample JSON artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build path-based DeepProgramSample JSON.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--sample-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.manifest.exists():
        print(f"error: manifest not found: {args.manifest}", file=sys.stderr)
        return 1
    print(f"manifest ready: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
