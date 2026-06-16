#!/usr/bin/env python3
"""Write Level 19 summary files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level18_archive_index import build_level18_archive_index
from traceleak.level19_summary import (
    build_level19_summary,
    render_level19_summary_report,
    write_level19_summary,
    write_level19_summary_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 19 summary files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level19_handoff_summary"), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = build_level19_summary(
            archive_index=build_level18_archive_index(),
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        report = render_level19_summary_report(summary)
        write_level19_summary(args.out_dir / "level19-summary.json", summary)
        write_level19_summary_report(args.out_dir / "level19-summary-report.md", report)
    except (OSError, ValueError) as exc:
        print(f"invalid level19 request: {exc}")
        return 1
    print(f"wrote level19 summary files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
