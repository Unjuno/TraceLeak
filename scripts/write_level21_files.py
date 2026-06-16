#!/usr/bin/env python3
"""Write Level 21 status-index files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level21_status_index import (
    build_level21_status_index,
    render_level21_status_index_report,
    write_level21_status_index,
    write_level21_status_index_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 21 status-index files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level21_status_index"), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        index = build_level21_status_index(
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        report = render_level21_status_index_report(index)
        write_level21_status_index(args.out_dir / "level21-status-index.json", index)
        write_level21_status_index_report(args.out_dir / "level21-status-index-report.md", report)
    except (OSError, ValueError) as exc:
        print(f"invalid level21 request: {exc}")
        return 1
    print(f"wrote level21 status-index files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
