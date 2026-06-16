"""Level 19 summary helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level18_archive_index import LEVEL18_ARCHIVE_INDEX_FORMAT, validate_level18_archive_index

LEVEL19_SUMMARY_FORMAT = "traceleak.level19_summary.v1"
LEVEL19_SUMMARY_PHASE = "P168"
LEVEL19_SUMMARY_REPORT_PHASE = "P169"
EXPECTED_LEVEL19_COMMANDS = [
    "pytest tests/test_level19_handoff_summary.py",
    "pytest tests/test_level19_handoff_summary_report.py",
    "pytest tests/test_write_level19_files_cli.py",
    "ruff check .",
    "pytest",
]
REVIEWED_LEVELS = ["level13", "level14", "level15", "level16", "level17", "level18"]


class Level19SummaryError(ValueError):
    """Raised when Level 19 summary data is invalid."""


def build_level19_summary(
    *,
    archive_index: dict[str, Any],
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    validate_level18_archive_index(archive_index)
    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    summary = {
        "format": LEVEL19_SUMMARY_FORMAT,
        "phase": LEVEL19_SUMMARY_PHASE,
        "source_index_format": archive_index["format"],
        "source_index_phase": archive_index["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "summary_status": "pending_local_validation",
        "source_archive_status": archive_index["archive_status"],
        "reviewed_levels": list(REVIEWED_LEVELS),
        "source_family_count": archive_index["family_count"],
        "source_path_count": archive_index["path_count"],
        "expected_validation_commands": list(EXPECTED_LEVEL19_COMMANDS),
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }
    validate_level19_summary(summary)
    return summary


def validate_level19_summary(summary: dict[str, Any]) -> None:
    if not isinstance(summary, dict):
        raise Level19SummaryError("summary must be an object")
    _eq(summary.get("format"), LEVEL19_SUMMARY_FORMAT, "summary.format")
    _eq(summary.get("phase"), LEVEL19_SUMMARY_PHASE, "summary.phase")
    _eq(summary.get("source_index_format"), LEVEL18_ARCHIVE_INDEX_FORMAT, "summary.source_index_format")
    _non_empty(summary.get("source_index_phase"), "summary.source_index_phase")
    _non_empty(summary.get("reviewer"), "summary.reviewer")
    _non_empty(summary.get("reviewed_at"), "summary.reviewed_at")
    _eq(summary.get("summary_status"), "pending_local_validation", "summary.summary_status")
    _eq(summary.get("source_archive_status"), "pending_local_validation", "summary.source_archive_status")
    _eq(summary.get("reviewed_levels"), REVIEWED_LEVELS, "summary.reviewed_levels")
    if not isinstance(summary.get("source_family_count"), int) or summary["source_family_count"] <= 0:
        raise Level19SummaryError("summary.source_family_count must be positive")
    if not isinstance(summary.get("source_path_count"), int) or summary["source_path_count"] <= 0:
        raise Level19SummaryError("summary.source_path_count must be positive")
    _eq(summary.get("expected_validation_commands"), EXPECTED_LEVEL19_COMMANDS, "summary.expected_validation_commands")
    flags = summary.get("flags")
    if not isinstance(flags, dict):
        raise Level19SummaryError("summary.flags must be an object")
    _eq(flags.get("review_only"), True, "summary.flags.review_only")
    _eq(flags.get("path_only"), True, "summary.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"summary.flags.{key}")


def render_level19_summary_report(summary: dict[str, Any]) -> str:
    validate_level19_summary(summary)
    lines = [
        "# Level 19 Summary Report",
        "",
        f"- Phase: `{LEVEL19_SUMMARY_REPORT_PHASE}`",
        f"- Summary status: `{summary['summary_status']}`",
        f"- Source archive status: `{summary['source_archive_status']}`",
        f"- Source index format: `{summary['source_index_format']}`",
        "",
        "## Reviewed levels",
        "",
    ]
    for level in summary["reviewed_levels"]:
        lines.append(f"- `{level}`")
    lines.extend([
        "",
        "## Review-only boundary",
        "",
        "Review only: `True`",
        "Path only: `True`",
        "Content read: `False`",
        "Command executed: `False`",
        "Claim generated: `False`",
        "",
        "## Expected validation commands",
        "",
    ])
    for command in summary["expected_validation_commands"]:
        lines.append(f"- `{command}`")
    lines.extend([
        "",
        "## Next-level preconditions",
        "",
        "- Focused Level 19 tests must pass locally.",
        "- `ruff check .` must pass locally.",
        "- Full `pytest` must pass locally.",
        "",
    ])
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level19_summary_report(markdown)
    return markdown


def validate_level19_summary_report(markdown: str) -> None:
    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level19SummaryError("markdown must be a newline-terminated string")
    for text in [
        "# Level 19 Summary Report",
        "## Reviewed levels",
        "## Review-only boundary",
        "## Expected validation commands",
        "## Next-level preconditions",
        "Review only: `True`",
        "Path only: `True`",
        "Content read: `False`",
        "Command executed: `False`",
        "Claim generated: `False`",
    ]:
        if text not in markdown:
            raise Level19SummaryError(f"missing markdown text: {text}")


def write_level19_summary(path: Path, summary: dict[str, Any]) -> None:
    validate_level19_summary(summary)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level19_summary_report(path: Path, markdown: str) -> None:
    validate_level19_summary_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level19SummaryError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level19SummaryError(f"{name} must be {expected!r}")
