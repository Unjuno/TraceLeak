"""Level 16 pre-handoff review helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level15_validation_rollup import (
    EXPECTED_VALIDATION_COMMANDS,
    LEVEL15_VALIDATION_ROLLUP_FORMAT,
    validate_level15_validation_rollup,
)

LEVEL16_PRE_HANDOFF_REVIEW_FORMAT = "traceleak.level16_pre_handoff_review.v1"
LEVEL16_PRE_HANDOFF_REVIEW_PHASE = "P153"
LEVEL16_PRE_HANDOFF_REVIEW_REPORT_PHASE = "P154"


class Level16PreHandoffReviewError(ValueError):
    """Raised when Level 16 pre-handoff review data is invalid."""


def build_level16_pre_handoff_review(
    *,
    validation_rollup: dict[str, Any],
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a pre-handoff review manifest from a Level 15 validation rollup."""

    validate_level15_validation_rollup(validation_rollup)
    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    source_status = validation_rollup["validation_status"]
    review = {
        "format": LEVEL16_PRE_HANDOFF_REVIEW_FORMAT,
        "phase": LEVEL16_PRE_HANDOFF_REVIEW_PHASE,
        "source_rollup_format": validation_rollup["format"],
        "source_rollup_phase": validation_rollup["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "source_validation_status": source_status,
        "source_completeness_status": validation_rollup["source_completeness_status"],
        "expected_validation_commands": list(validation_rollup["expected_validation_commands"]),
        "review_disposition": (
            "ready_after_local_validation"
            if source_status == "pending"
            else "blocked_by_validation_state"
        ),
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }
    validate_level16_pre_handoff_review(review)
    return review


def validate_level16_pre_handoff_review(review: dict[str, Any]) -> None:
    """Validate Level 16 pre-handoff review shape."""

    if not isinstance(review, dict):
        raise Level16PreHandoffReviewError("review must be an object")
    _eq(review.get("format"), LEVEL16_PRE_HANDOFF_REVIEW_FORMAT, "review.format")
    _eq(review.get("phase"), LEVEL16_PRE_HANDOFF_REVIEW_PHASE, "review.phase")
    _eq(
        review.get("source_rollup_format"),
        LEVEL15_VALIDATION_ROLLUP_FORMAT,
        "review.source_rollup_format",
    )
    _non_empty(review.get("source_rollup_phase"), "review.source_rollup_phase")
    _non_empty(review.get("reviewer"), "review.reviewer")
    _non_empty(review.get("reviewed_at"), "review.reviewed_at")
    _eq(review.get("source_validation_status"), "pending", "review.source_validation_status")
    if review.get("source_completeness_status") not in {"complete", "incomplete"}:
        raise Level16PreHandoffReviewError("review.source_completeness_status is invalid")
    _eq(
        review.get("expected_validation_commands"),
        EXPECTED_VALIDATION_COMMANDS,
        "review.expected_validation_commands",
    )
    _eq(
        review.get("review_disposition"),
        "ready_after_local_validation",
        "review.review_disposition",
    )
    flags = review.get("flags")
    if not isinstance(flags, dict):
        raise Level16PreHandoffReviewError("review.flags must be an object")
    _eq(flags.get("review_only"), True, "review.flags.review_only")
    _eq(flags.get("path_only"), True, "review.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"review.flags.{key}")


def render_level16_pre_handoff_review_report(review: dict[str, Any]) -> str:
    """Render a Markdown report for Level 16 pre-handoff review."""

    validate_level16_pre_handoff_review(review)
    lines = [
        "# Level 16 Pre-Handoff Review Report",
        "",
        f"- Phase: `{LEVEL16_PRE_HANDOFF_REVIEW_REPORT_PHASE}`",
        f"- Review disposition: `{review['review_disposition']}`",
        f"- Source validation status: `{review['source_validation_status']}`",
        f"- Source completeness status: `{review['source_completeness_status']}`",
        "",
        "## Expected validation commands",
        "",
    ]
    for command in review["expected_validation_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(
        [
            "",
            "## Review-only boundary",
            "",
            "Review only: `True`",
            "Path only: `True`",
            "Content read: `False`",
            "Command executed: `False`",
            "Claim generated: `False`",
            "",
            "## Local validation commands",
            "",
            "```powershell",
            "pytest tests/test_level16_pre_handoff_review.py",
            "pytest tests/test_level16_review_report.py",
            "pytest tests/test_write_level16_files_cli.py",
            "ruff check .",
            "pytest",
            "```",
            "",
            "## Next-level preconditions",
            "",
            "- Focused Level 16 tests must pass locally.",
            "- `ruff check .` must pass locally.",
            "- Full `pytest` must pass locally.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level16_pre_handoff_review_report(markdown)
    return markdown


def validate_level16_pre_handoff_review_report(markdown: str) -> None:
    """Validate Level 16 pre-handoff review Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level16PreHandoffReviewError("markdown must be a newline-terminated string")
    for text in [
        "# Level 16 Pre-Handoff Review Report",
        "## Expected validation commands",
        "## Review-only boundary",
        "## Local validation commands",
        "## Next-level preconditions",
        "Review only: `True`",
        "Path only: `True`",
        "Content read: `False`",
        "Command executed: `False`",
        "Claim generated: `False`",
    ]:
        if text not in markdown:
            raise Level16PreHandoffReviewError(f"missing markdown text: {text}")


def write_level16_pre_handoff_review(path: Path, review: dict[str, Any]) -> None:
    """Write Level 16 pre-handoff review JSON."""

    validate_level16_pre_handoff_review(review)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level16_pre_handoff_review_report(path: Path, markdown: str) -> None:
    """Write Level 16 pre-handoff review Markdown report."""

    validate_level16_pre_handoff_review_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level16PreHandoffReviewError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level16PreHandoffReviewError(f"{name} must be {expected!r}")
