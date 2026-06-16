#!/usr/bin/env python3
"""Write Level 16 local review files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

LEVEL16_LOCAL_REVIEW_FORMAT = "traceleak.level16_local_review.v1"
LEVEL16_LOCAL_REVIEW_PHASE = "P155"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 16 local review files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level16_review"), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    return parser.parse_args()


def build_local_review(*, reviewer: str, reviewed_at: str) -> dict:
    reviewer = reviewer.strip()
    reviewed_at = reviewed_at.strip()
    if not reviewer:
        raise ValueError("reviewer must be non-empty")
    if not reviewed_at:
        raise ValueError("reviewed_at must be non-empty")
    return {
        "format": LEVEL16_LOCAL_REVIEW_FORMAT,
        "phase": LEVEL16_LOCAL_REVIEW_PHASE,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
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


def render_local_review_report(review: dict) -> str:
    lines = [
        "# Level 16 Local Review",
        "",
        f"- Phase: `{review['phase']}`",
        f"- Status: `{review['status']}`",
        "",
        "## Expected validation commands",
        "",
    ]
    for command in review["expected_validation_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Review only: `True`",
            "Path only: `True`",
            "Content read: `False`",
            "Command executed: `False`",
            "Claim generated: `False`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        review = build_local_review(reviewer=args.reviewer, reviewed_at=args.reviewed_at)
        report = render_local_review_report(review)
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "level16-review.json").write_text(
            json.dumps(review, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (args.out_dir / "level16-review-report.md").write_text(report, encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"invalid level16 request: {exc}")
        return 1
    print(f"wrote level16 review files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
