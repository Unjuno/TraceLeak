#!/usr/bin/env python3
"""Write the local metadata-only report bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.local_report_bundle import run_local_report_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the local metadata-only report bundle.")
    parser.add_argument("--root-dir", default=Path("reports/local"), type=Path)
    parser.add_argument("--record-count", default=4, type=int)
    parser.add_argument("--epochs", default=20, type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = run_local_report_bundle(
            root_dir=args.root_dir,
            record_count=args.record_count,
            epochs=args.epochs,
        )
    except Exception as exc:
        print(f"invalid local report bundle request: {exc}")
        return 1
    print(f"wrote local report bundle: {summary['root_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
