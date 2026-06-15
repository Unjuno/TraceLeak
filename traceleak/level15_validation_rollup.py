"""Level 15 validation rollup helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level14_completeness import (
    LEVEL14_COMPLETENESS_AUDIT_FORMAT,
    validate_level14_completeness_audit,
)

LEVEL15_VALIDATION_ROLLUP_FORMAT = "traceleak.level15_validation_rollup.v1"
LEVEL15_VALIDATION_ROLLUP_PHASE = "P148"
LEVEL15_VALIDATION_ROLLUP_REPORT_PHASE = "P149"
EXPECTED_VALIDATION_COMMANDS = [
    "pytest tests/test_level15_validation_rollup.py",
    "pytest tests/test_level15_validation_rollup_report.py",
    "pytest tests/test_write_level15_files_cli.py",
    "ruff check .",
    "pytest",
]


class Level15ValidationRollupError(ValueError):
    """Raised when Level 15 validation rollup data is invalid."""


def build_level15_validation_rollup(
    *,
    completeness_audit: dict[str, Any],
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a pending validation rollup from a Level 14 completeness audit."""

    validate_level14_completeness_audit(completeness_audit)
    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    rollup = {
        "format": LEVEL15_VALIDATION_ROLLUP_FORMAT,
        "phase": LEVEL15_VALIDATION_ROLLUP_PHASE,
        "source_audit_format": completeness_audit["format"],
        "source_audit_phase": completeness_audit["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "source_completeness_status": completeness_audit["completeness_status"],
        "validation_status": "pending",
        "expected_validation_commands": list(EXPECTED_VALIDATION_COMMANDS),
        "validation_results": [
            {"command": command, "status": "pending"} for command in EXPECTED_VALIDATION_COMMANDS
        ],
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }
    validate_level15_validation_rollup(rollup)
    return rollup


def validate_level15_validation_rollup(rollup: dict[str, Any]) -> None:
    """Validate Level 15 validation rollup shape."""

    if not isinstance(rollup, dict):
        raise Level15ValidationRollupError("rollup must be an object")
    _eq(rollup.get("format"), LEVEL15_VALIDATION_ROLLUP_FORMAT, "rollup.format")
    _eq(rollup.get("phase"), LEVEL15_VALIDATION_ROLLUP_PHASE, "rollup.phase")
    _eq(
        rollup.get("source_audit_format"),
        LEVEL14_COMPLETENESS_AUDIT_FORMAT,
        "rollup.source_audit_format",
    )
    _non_empty(rollup.get("source_audit_phase"), "rollup.source_audit_phase")
    _non_empty(rollup.get("reviewer"), "rollup.reviewer")
    _non_empty(rollup.get("reviewed_at"), "rollup.reviewed_at")
    if rollup.get("source_completeness_status") not in {"complete", "incomplete"}:
        raise Level15ValidationRollupError("rollup.source_completeness_status is invalid")
    _eq(rollup.get("validation_status"), "pending", "rollup.validation_status")
    _eq(
        rollup.get("expected_validation_commands"),
        EXPECTED_VALIDATION_COMMANDS,
        "rollup.expected_validation_commands",
    )
    results = rollup.get("validation_results")
    if not isinstance(results, list) or len(results) != len(EXPECTED_VALIDATION_COMMANDS):
        raise Level15ValidationRollupError("rollup.validation_results has invalid length")
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            raise Level15ValidationRollupError(f"rollup.validation_results[{index}] must be an object")
        _eq(item.get("command"), EXPECTED_VALIDATION_COMMANDS[index], f"rollup.validation_results[{index}].command")
        _eq(item.get("status"), "pending", f"rollup.validation_results[{index}].status")
    flags = rollup.get("flags")
    if not isinstance(flags, dict):
        raise Level15ValidationRollupError("rollup.flags must be an object")
    _eq(flags.get("review_only"), True, "rollup.flags.review_only")
    _eq(flags.get("path_only"), True, "rollup.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"rollup.flags.{key}")


def render_level15_validation_rollup_report(rollup: dict[str, Any]) -> str:
    """Render a Markdown report for Level 15 validation rollup."""

    validate_level15_validation_rollup(rollup)
    lines = [
        "# Level 15 Validation Rollup Report",
        "",
        f"- Phase: `{LEVEL15_VALIDATION_ROLLUP_REPORT_PHASE}`",
        f"- Rollup status: `{rollup['validation_status']}`",
        f"- Source completeness status: `{rollup['source_completeness_status']}`",
        "",
        "## Expected validation commands",
        "",
    ]
    for command in rollup["expected_validation_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(
        [
            "",
            "## Pending validation state",
            "",
            "Validation status: `pending`",
            "Commands executed: `False`",
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
            "- Focused Level 15 tests must pass locally.",
            "- `ruff check .` must pass locally.",
            "- Full `pytest` must pass locally.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level15_validation_rollup_report(markdown)
    return markdown


def validate_level15_validation_rollup_report(markdown: str) -> None:
    """Validate Level 15 validation rollup Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level15ValidationRollupError("markdown must be a newline-terminated string")
    for text in [
        "# Level 15 Validation Rollup Report",
        "## Expected validation commands",
        "## Pending validation state",
        "## Review-only boundary",
        "## Next-level preconditions",
        "Review only: `True`",
        "Path only: `True`",
        "Content read: `False`",
        "Command executed: `False`",
        "Claim generated: `False`",
    ]:
        if text not in markdown:
            raise Level15ValidationRollupError(f"missing markdown text: {text}")


def write_level15_validation_rollup(path: Path, rollup: dict[str, Any]) -> None:
    """Write Level 15 validation rollup JSON."""

    validate_level15_validation_rollup(rollup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rollup, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level15_validation_rollup_report(path: Path, markdown: str) -> None:
    """Write Level 15 validation rollup Markdown report."""

    validate_level15_validation_rollup_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level15ValidationRollupError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level15ValidationRollupError(f"{name} must be {expected!r}")
