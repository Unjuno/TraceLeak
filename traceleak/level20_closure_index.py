"""Level 20 closure-index helpers."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

LEVEL20_CLOSURE_INDEX_FORMAT = "traceleak.level20_closure_index.v1"
LEVEL20_CLOSURE_INDEX_PHASE = "P173"
LEVEL20_CLOSURE_INDEX_REPORT_PHASE = "P174"
EXPECTED_LEVEL20_COMMANDS = [
    "pytest tests/test_level20_closure_index.py",
    "pytest tests/test_level20_closure_index_report.py",
    "pytest tests/test_write_level20_files_cli.py",
    "ruff check .",
    "pytest",
]
DEFAULT_LEVEL19_OUTPUT_PATHS = [
    "reports/local/level19_handoff_summary/level19-summary.json",
    "reports/local/level19_handoff_summary/level19-summary-report.md",
]


class Level20ClosureIndexError(ValueError):
    """Raised when Level 20 closure-index data is invalid."""


def build_level20_closure_index(
    *,
    output_paths: list[str] | None = None,
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a path-only closure index for Level 19 outputs."""

    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    paths = [str(path) for path in (output_paths or DEFAULT_LEVEL19_OUTPUT_PATHS)]
    index = {
        "format": LEVEL20_CLOSURE_INDEX_FORMAT,
        "phase": LEVEL20_CLOSURE_INDEX_PHASE,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "closure_status": "pending_local_validation",
        "output_paths": paths,
        "path_count": len(paths),
        "expected_validation_commands": list(EXPECTED_LEVEL20_COMMANDS),
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }
    validate_level20_closure_index(index)
    return index


def validate_level20_closure_index(index: dict[str, Any]) -> None:
    """Validate Level 20 closure-index shape."""

    if not isinstance(index, dict):
        raise Level20ClosureIndexError("index must be an object")
    _eq(index.get("format"), LEVEL20_CLOSURE_INDEX_FORMAT, "index.format")
    _eq(index.get("phase"), LEVEL20_CLOSURE_INDEX_PHASE, "index.phase")
    _non_empty(index.get("reviewer"), "index.reviewer")
    _non_empty(index.get("reviewed_at"), "index.reviewed_at")
    _eq(index.get("closure_status"), "pending_local_validation", "index.closure_status")
    paths = index.get("output_paths")
    if not isinstance(paths, list) or not paths:
        raise Level20ClosureIndexError("index.output_paths must be a non-empty list")
    for path in paths:
        _validate_relative_report_path(path)
    _eq(index.get("path_count"), len(paths), "index.path_count")
    _eq(
        index.get("expected_validation_commands"),
        EXPECTED_LEVEL20_COMMANDS,
        "index.expected_validation_commands",
    )
    flags = index.get("flags")
    if not isinstance(flags, dict):
        raise Level20ClosureIndexError("index.flags must be an object")
    _eq(flags.get("review_only"), True, "index.flags.review_only")
    _eq(flags.get("path_only"), True, "index.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"index.flags.{key}")


def render_level20_closure_index_report(index: dict[str, Any]) -> str:
    """Render a Markdown report for Level 20 closure index."""

    validate_level20_closure_index(index)
    lines = [
        "# Level 20 Closure Index Report",
        "",
        f"- Phase: `{LEVEL20_CLOSURE_INDEX_REPORT_PHASE}`",
        f"- Closure status: `{index['closure_status']}`",
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
            "- Focused Level 20 tests must pass locally.",
            "- `ruff check .` must pass locally.",
            "- Full `pytest` must pass locally.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level20_closure_index_report(markdown)
    return markdown


def validate_level20_closure_index_report(markdown: str) -> None:
    """Validate Level 20 closure-index Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level20ClosureIndexError("markdown must be a newline-terminated string")
    for text in [
        "# Level 20 Closure Index Report",
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
            raise Level20ClosureIndexError(f"missing markdown text: {text}")


def write_level20_closure_index(path: Path, index: dict[str, Any]) -> None:
    """Write Level 20 closure-index JSON."""

    validate_level20_closure_index(index)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level20_closure_index_report(path: Path, markdown: str) -> None:
    """Write Level 20 closure-index Markdown report."""

    validate_level20_closure_index_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _validate_relative_report_path(value: Any) -> str:
    path = _non_empty(value, "path")
    parsed = PurePosixPath(path.replace("\\", "/"))
    if parsed.is_absolute():
        raise Level20ClosureIndexError("path must be relative")
    if ".." in parsed.parts:
        raise Level20ClosureIndexError("path must not contain parent-directory segments")
    if len(parsed.parts) < 3 or parsed.parts[:2] != ("reports", "local"):
        raise Level20ClosureIndexError("path must stay under reports/local")
    return path


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level20ClosureIndexError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level20ClosureIndexError(f"{name} must be {expected!r}")
