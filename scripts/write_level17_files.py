#!/usr/bin/env python3
"""Write Level 17 release-readiness files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level17_release_readiness import (
    LEVEL16_LOCAL_REVIEW_FORMAT,
    build_level17_release_readiness,
    render_level17_release_readiness_report,
    write_level17_release_readiness,
    write_level17_release_readiness_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 17 release-readiness files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level17_release_readiness"), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    return parser.parse_args()


def build_default_level16_review() -> dict:
    return {
        "format": LEVEL16_LOCAL_REVIEW_FORMAT,
        "phase": "P155",
        "reviewer": "reviewer",
        "reviewed_at": "2026-06-15T00:00:00Z",
        "status": "pending_local_validation",
        "expected_validation_commands": [
            "pytest tests/test_level16_pre_handoff_review.py",
            "pytest tests/test_level16_review_report.py",
            "pytest tests/test_write_level16_files_cli.py",
            "ruff check .",
            "pytest",
        ],
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }


def main() -> int:
    args = parse_args()
    try:
        checklist = build_level17_release_readiness(
            level16_review=build_default_level16_review(),
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        report = render_level17_release_readiness_report(checklist)
        write_level17_release_readiness(
            args.out_dir / "level17-release-readiness.json",
            checklist,
        )
        write_level17_release_readiness_report(
            args.out_dir / "level17-release-readiness-report.md",
            report,
        )
    except (OSError, ValueError) as exc:
        print(f"invalid level17 request: {exc}")
        return 1
    print(f"wrote level17 release-readiness files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
