#!/usr/bin/env python3
"""Write Level 18 archive-index files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level18_archive_index import (
    build_level18_archive_index,
    render_level18_archive_index_report,
    write_level18_archive_index,
    write_level18_archive_index_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 18 archive-index files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level18_archive_index"), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        index = build_level18_archive_index(
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        report = render_level18_archive_index_report(index)
        write_level18_archive_index(args.out_dir / "level18-archive-index.json", index)
        write_level18_archive_index_report(
            args.out_dir / "level18-archive-index-report.md",
            report,
        )
    except (OSError, ValueError) as exc:
        print(f"invalid level18 request: {exc}")
        return 1
    print(f"wrote level18 archive-index files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
