"""Level 24 path-index helpers."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

LEVEL24_INDEX_FORMAT = "traceleak.level24_index.v1"
LEVEL24_INDEX_PHASE = "P193"
LEVEL24_INDEX_REPORT_PHASE = "P194"
EXPECTED_LEVEL24_COMMANDS = [
    "pytest tests/test_level24_index.py",
    "pytest tests/test_level24_index_report.py",
    "pytest tests/test_write_level24_files_cli.py",
    "ruff check .",
    "pytest",
]
DEFAULT_LEVEL23_OUTPUT_PATHS = [
    "reports/local/level23_index/level23-index.json",
    "reports/local/level23_index/level23-index-report.md",
]


class Level24IndexError(ValueError):
    """Raised when Level 24 index data is invalid."""


def build_level24_index(
    *,
    output_paths: list[str] | None = None,
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a path-only index for Level 23 outputs."""

    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    paths = [str(path) for path in (output_paths or DEFAULT_LEVEL23_OUTPUT_PATHS)]
    index = {
        "format": LEVEL24_INDEX_FORMAT,
        "phase": LEVEL24_INDEX_PHASE,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "status": "pending_local_validation",
        "output_paths": paths,
        "path_count": len(paths),
        "expected_validation_commands": list(EXPECTED_LEVEL24_COMMANDS),
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }
    validate_level24_index(index)
    return index


def validate_level24_index(index: dict[str, Any]) -> None:
    """Validate Level 24 index shape."""

    if not isinstance(index, dict):
        raise Level24IndexError("index must be an object")
    _eq(index.get("format"), LEVEL24_INDEX_FORMAT, "index.format")
    _eq(index.get("phase"), LEVEL24_INDEX_PHASE, "index.phase")
    _non_empty(index.get("reviewer"), "index.reviewer")
    _non_empty(index.get("reviewed_at"), "index.reviewed_at")
    _eq(index.get("status"), "pending_local_validation", "index.status")
    paths = index.get("output_paths")
    if not isinstance(paths, list) or not paths:
        raise Level24IndexError("index.output_paths must be a non-empty list")
    for path in paths:
        _validate_relative_report_path(path)
    _eq(index.get("path_count"), len(paths), "index.path_count")
    _eq(
        index.get("expected_validation_commands"),
        EXPECTED_LEVEL24_COMMANDS,
        "index.expected_validation_commands",
    )
    flags = index.get("flags")
    if not isinstance(flags, dict):
        raise Level24IndexError("index.flags must be an object")
    _eq(flags.get("review_only"), True, "index.flags.review_only")
    _eq(flags.get("path_only"), True, "index.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"index.flags.{key}")


def render_level24_index_report(index: dict[str, Any]) -> str:
    """Render a Markdown report for Level 24 index."""

    validate_level24_index(index)
    lines = [
        "# Level 24 Index Report",
        "",
        f"- Phase: `{LEVEL24_INDEX_REPORT_PHASE}`",
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
            "- Focused Level 24 tests must pass locally.",
            "- `ruff check .` must pass locally.",
            "- Full `pytest` must pass locally.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level24_index_report(markdown)
    return markdown


def validate_level24_index_report(markdown: str) -> None:
    """Validate Level 24 Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level24IndexError("markdown must be a newline-terminated string")
    for text in [
        "# Level 24 Index Report",
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
            raise Level24IndexError(f"missing markdown text: {text}")


def write_level24_index(path: Path, index: dict[str, Any]) -> None:
    """Write Level 24 index JSON."""

    validate_level24_index(index)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level24_index_report(path: Path, markdown: str) -> None:
    """Write Level 24 Markdown report."""

    validate_level24_index_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _validate_relative_report_path(value: Any) -> str:
    path = _non_empty(value, "path")
    parsed = PurePosixPath(path.replace("\\", "/"))
    if parsed.is_absolute():
        raise Level24IndexError("path must be relative")
    if ".." in parsed.parts:
        raise Level24IndexError("path must not contain parent-directory segments")
    if len(parsed.parts) < 3 or parsed.parts[:2] != ("reports", "local"):
        raise Level24IndexError("path must stay under reports/local")
    return path


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level24IndexError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level24IndexError(f"{name} must be {expected!r}")
