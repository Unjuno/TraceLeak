#!/usr/bin/env python3
"""Write Level 20 closure-index files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level20_closure_index import (
    build_level20_closure_index,
    render_level20_closure_index_report,
    write_level20_closure_index,
    write_level20_closure_index_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 20 closure-index files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level20_closure_index"), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        index = build_level20_closure_index(
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        report = render_level20_closure_index_report(index)
        write_level20_closure_index(args.out_dir / "level20-closure-index.json", index)
        write_level20_closure_index_report(
            args.out_dir / "level20-closure-index-report.md",
            report,
        )
    except (OSError, ValueError) as exc:
        print(f"invalid level20 request: {exc}")
        return 1
    print(f"wrote level20 closure-index files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
