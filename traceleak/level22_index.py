"""Level 22 path-index helpers."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

LEVEL22_INDEX_FORMAT = "traceleak.level22_index.v1"
LEVEL22_INDEX_PHASE = "P183"
LEVEL22_INDEX_REPORT_PHASE = "P184"
EXPECTED_LEVEL22_COMMANDS = [
    "pytest tests/test_level22_index.py",
    "pytest tests/test_level22_index_report.py",
    "pytest tests/test_write_level22_files_cli.py",
    "ruff check .",
    "pytest",
]
DEFAULT_LEVEL21_OUTPUT_PATHS = [
    "reports/local/level21_status_index/level21-status-index.json",
    "reports/local/level21_status_index/level21-status-index-report.md",
]


class Level22IndexError(ValueError):
    """Raised when Level 22 index data is invalid."""


def build_level22_index(
    *,
    output_paths: list[str] | None = None,
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a path-only index for Level 21 outputs."""

    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    paths = [str(path) for path in (output_paths or DEFAULT_LEVEL21_OUTPUT_PATHS)]
    index = {
        "format": LEVEL22_INDEX_FORMAT,
        "phase": LEVEL22_INDEX_PHASE,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "status": "pending_local_validation",
        "output_paths": paths,
        "path_count": len(paths),
        "expected_validation_commands": list(EXPECTED_LEVEL22_COMMANDS),
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }
    validate_level22_index(index)
    return index


def validate_level22_index(index: dict[str, Any]) -> None:
    """Validate Level 22 index shape."""

    if not isinstance(index, dict):
        raise Level22IndexError("index must be an object")
    _eq(index.get("format"), LEVEL22_INDEX_FORMAT, "index.format")
    _eq(index.get("phase"), LEVEL22_INDEX_PHASE, "index.phase")
    _non_empty(index.get("reviewer"), "index.reviewer")
    _non_empty(index.get("reviewed_at"), "index.reviewed_at")
    _eq(index.get("status"), "pending_local_validation", "index.status")
    paths = index.get("output_paths")
    if not isinstance(paths, list) or not paths:
        raise Level22IndexError("index.output_paths must be a non-empty list")
    for path in paths:
        _validate_relative_report_path(path)
    _eq(index.get("path_count"), len(paths), "index.path_count")
    _eq(
        index.get("expected_validation_commands"),
        EXPECTED_LEVEL22_COMMANDS,
        "index.expected_validation_commands",
    )
    flags = index.get("flags")
    if not isinstance(flags, dict):
        raise Level22IndexError("index.flags must be an object")
    _eq(flags.get("review_only"), True, "index.flags.review_only")
    _eq(flags.get("path_only"), True, "index.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"index.flags.{key}")


def render_level22_index_report(index: dict[str, Any]) -> str:
    """Render a Markdown report for Level 22 index."""

    validate_level22_index(index)
    lines = [
        "# Level 22 Index Report",
        "",
        f"- Phase: `{LEVEL22_INDEX_REPORT_PHASE}`",
        f"- Status: `{index['status']}`",
        f"- Path count: `{index['path_count']}`",
        "",
        "## Output paths",
        "",
    ]
    for path in index["output_paths"]:
        lines.append(f"- `{path}`")
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
            "## Expected validation commands",
            "",
        ]
    )
    for command in index["expected_validation_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(
        [
            "",
            "## Next-level preconditions",
            "",
            "- Focused Level 22 tests must pass locally.",
            "- `ruff check .` must pass locally.",
            "- Full `pytest` must pass locally.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level22_index_report(markdown)
    return markdown


def validate_level22_index_report(markdown: str) -> None:
    """Validate Level 22 Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level22IndexError("markdown must be a newline-terminated string")
    for text in [
        "# Level 22 Index Report",
        "## Output paths",
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
            raise Level22IndexError(f"missing markdown text: {text}")


def write_level22_index(path: Path, index: dict[str, Any]) -> None:
    """Write Level 22 index JSON."""

    validate_level22_index(index)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level22_index_report(path: Path, markdown: str) -> None:
    """Write Level 22 Markdown report."""

    validate_level22_index_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _validate_relative_report_path(value: Any) -> str:
    path = _non_empty(value, "path")
    parsed = PurePosixPath(path.replace("\\", "/"))
    if parsed.is_absolute():
        raise Level22IndexError("path must be relative")
    if ".." in parsed.parts:
        raise Level22IndexError("path must not contain parent-directory segments")
    if len(parsed.parts) < 3 or parsed.parts[:2] != ("reports", "local"):
        raise Level22IndexError("path must stay under reports/local")
    return path


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level22IndexError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level22IndexError(f"{name} must be {expected!r}")
