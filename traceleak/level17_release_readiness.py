"""Level 17 release-readiness helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LEVEL16_LOCAL_REVIEW_FORMAT = "traceleak.level16_local_review.v1"
LEVEL17_RELEASE_READINESS_FORMAT = "traceleak.level17_release_readiness.v1"
LEVEL17_RELEASE_READINESS_PHASE = "P158"
LEVEL17_RELEASE_READINESS_REPORT_PHASE = "P159"
EXPECTED_LEVEL17_COMMANDS = [
    "pytest tests/test_level17_release_readiness.py",
    "pytest tests/test_level17_release_readiness_report.py",
    "pytest tests/test_write_level17_files_cli.py",
    "ruff check .",
    "pytest",
]
READINESS_ITEMS = [
    "focused_tests",
    "ruff",
    "full_pytest",
    "docs_updated",
]


class Level17ReleaseReadinessError(ValueError):
    """Raised when Level 17 release-readiness data is invalid."""


def build_level17_release_readiness(
    *,
    level16_review: dict[str, Any],
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a review-only release-readiness checklist from a Level 16 review."""

    validate_level16_local_review(level16_review)
    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    checklist = {
        "format": LEVEL17_RELEASE_READINESS_FORMAT,
        "phase": LEVEL17_RELEASE_READINESS_PHASE,
        "source_review_format": level16_review["format"],
        "source_review_phase": level16_review["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "source_review_status": level16_review["status"],
        "readiness_status": "pending_local_validation",
        "expected_validation_commands": list(EXPECTED_LEVEL17_COMMANDS),
        "readiness_items": [
            {"name": item, "status": "pending"} for item in READINESS_ITEMS
        ],
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }
    validate_level17_release_readiness(checklist)
    return checklist


def validate_level16_local_review(review: dict[str, Any]) -> None:
    """Validate the minimal Level 16 local review artifact used by Level 17."""

    if not isinstance(review, dict):
        raise Level17ReleaseReadinessError("level16 review must be an object")
    _eq(review.get("format"), LEVEL16_LOCAL_REVIEW_FORMAT, "level16_review.format")
    _non_empty(review.get("phase"), "level16_review.phase")
    _non_empty(review.get("reviewer"), "level16_review.reviewer")
    _non_empty(review.get("reviewed_at"), "level16_review.reviewed_at")
    _eq(review.get("status"), "pending_local_validation", "level16_review.status")
    commands = review.get("expected_validation_commands")
    if not isinstance(commands, list) or not commands:
        raise Level17ReleaseReadinessError(
            "level16_review.expected_validation_commands must be a non-empty list"
        )
    for command in commands:
        _non_empty(command, "level16_review.expected_validation_commands[]")
    flags = review.get("flags")
    if not isinstance(flags, dict):
        raise Level17ReleaseReadinessError("level16_review.flags must be an object")
    _eq(flags.get("review_only"), True, "level16_review.flags.review_only")
    _eq(flags.get("path_only"), True, "level16_review.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"level16_review.flags.{key}")


def validate_level17_release_readiness(checklist: dict[str, Any]) -> None:
    """Validate Level 17 release-readiness checklist shape."""

    if not isinstance(checklist, dict):
        raise Level17ReleaseReadinessError("checklist must be an object")
    _eq(checklist.get("format"), LEVEL17_RELEASE_READINESS_FORMAT, "checklist.format")
    _eq(checklist.get("phase"), LEVEL17_RELEASE_READINESS_PHASE, "checklist.phase")
    _eq(
        checklist.get("source_review_format"),
        LEVEL16_LOCAL_REVIEW_FORMAT,
        "checklist.source_review_format",
    )
    _non_empty(checklist.get("source_review_phase"), "checklist.source_review_phase")
    _non_empty(checklist.get("reviewer"), "checklist.reviewer")
    _non_empty(checklist.get("reviewed_at"), "checklist.reviewed_at")
    _eq(
        checklist.get("source_review_status"),
        "pending_local_validation",
        "checklist.source_review_status",
    )
    _eq(
        checklist.get("readiness_status"),
        "pending_local_validation",
        "checklist.readiness_status",
    )
    _eq(
        checklist.get("expected_validation_commands"),
        EXPECTED_LEVEL17_COMMANDS,
        "checklist.expected_validation_commands",
    )
    items = checklist.get("readiness_items")
    if not isinstance(items, list) or len(items) != len(READINESS_ITEMS):
        raise Level17ReleaseReadinessError("checklist.readiness_items has invalid length")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise Level17ReleaseReadinessError(
                f"checklist.readiness_items[{index}] must be an object"
            )
        _eq(item.get("name"), READINESS_ITEMS[index], f"checklist.readiness_items[{index}].name")
        _eq(item.get("status"), "pending", f"checklist.readiness_items[{index}].status")
    flags = checklist.get("flags")
    if not isinstance(flags, dict):
        raise Level17ReleaseReadinessError("checklist.flags must be an object")
    _eq(flags.get("review_only"), True, "checklist.flags.review_only")
    _eq(flags.get("path_only"), True, "checklist.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"checklist.flags.{key}")


def render_level17_release_readiness_report(checklist: dict[str, Any]) -> str:
    """Render a Markdown report for Level 17 release-readiness."""

    validate_level17_release_readiness(checklist)
    lines = [
        "# Level 17 Release-Readiness Report",
        "",
        f"- Phase: `{LEVEL17_RELEASE_READINESS_REPORT_PHASE}`",
        f"- Readiness status: `{checklist['readiness_status']}`",
        f"- Source review status: `{checklist['source_review_status']}`",
        "",
        "## Readiness items",
        "",
    ]
    for item in checklist["readiness_items"]:
        lines.append(f"- `{item['name']}`: `{item['status']}`")
    lines.extend(["", "## Expected validation commands", ""])
    for command in checklist["expected_validation_commands"]:
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
            "## Next-level preconditions",
            "",
            "- Focused Level 17 tests must pass locally.",
            "- `ruff check .` must pass locally.",
            "- Full `pytest` must pass locally.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level17_release_readiness_report(markdown)
    return markdown


def validate_level17_release_readiness_report(markdown: str) -> None:
    """Validate Level 17 release-readiness Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level17ReleaseReadinessError("markdown must be a newline-terminated string")
    for text in [
        "# Level 17 Release-Readiness Report",
        "## Readiness items",
        "## Expected validation commands",
        "## Review-only boundary",
        "## Next-level preconditions",
        "Review only: `True`",
        "Path only: `True`",
        "Content read: `False`",
        "Command executed: `False`",
        "Claim generated: `False`",
    ]:
        if text not in markdown:
            raise Level17ReleaseReadinessError(f"missing markdown text: {text}")


def write_level17_release_readiness(path: Path, checklist: dict[str, Any]) -> None:
    """Write Level 17 release-readiness JSON."""

    validate_level17_release_readiness(checklist)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checklist, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level17_release_readiness_report(path: Path, markdown: str) -> None:
    """Write Level 17 release-readiness Markdown report."""

    validate_level17_release_readiness_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level17ReleaseReadinessError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level17ReleaseReadinessError(f"{name} must be {expected!r}")
