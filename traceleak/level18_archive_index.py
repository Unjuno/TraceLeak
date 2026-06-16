"""Level 18 archive-index helpers."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

LEVEL18_ARCHIVE_INDEX_FORMAT = "traceleak.level18_archive_index.v1"
LEVEL18_ARCHIVE_INDEX_PHASE = "P163"
LEVEL18_ARCHIVE_INDEX_REPORT_PHASE = "P164"
EXPECTED_LEVEL18_COMMANDS = [
    "pytest tests/test_level18_archive_index.py",
    "pytest tests/test_level18_archive_index_report.py",
    "pytest tests/test_write_level18_files_cli.py",
    "ruff check .",
    "pytest",
]
DEFAULT_ARCHIVE_FAMILIES = [
    {
        "family": "level13_closure",
        "paths": [
            "reports/local/level13_closure/level13-closure-manifest.json",
            "reports/local/level13_closure/level13-handoff-inventory.json",
            "reports/local/level13_closure/level13-closure-report.md",
        ],
    },
    {
        "family": "level14_completeness",
        "paths": [
            "reports/local/level14_completeness/level14-completeness-audit.json",
            "reports/local/level14_completeness/level14-completeness-report.md",
        ],
    },
    {
        "family": "level15_validation_rollup",
        "paths": [
            "reports/local/level15_validation_rollup/level15-validation-rollup.json",
            "reports/local/level15_validation_rollup/level15-validation-rollup-report.md",
        ],
    },
    {
        "family": "level16_review",
        "paths": [
            "reports/local/level16_review/level16-review.json",
            "reports/local/level16_review/level16-review-report.md",
        ],
    },
    {
        "family": "level17_release_readiness",
        "paths": [
            "reports/local/level17_release_readiness/level17-release-readiness.json",
            "reports/local/level17_release_readiness/level17-release-readiness-report.md",
        ],
    },
]


class Level18ArchiveIndexError(ValueError):
    """Raised when Level 18 archive-index data is invalid."""


def build_level18_archive_index(
    *,
    families: list[dict[str, Any]] | None = None,
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a path-only archive index for local review artifacts."""

    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    archive_families = _copy_families(families or DEFAULT_ARCHIVE_FAMILIES)
    index = {
        "format": LEVEL18_ARCHIVE_INDEX_FORMAT,
        "phase": LEVEL18_ARCHIVE_INDEX_PHASE,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "archive_status": "pending_local_validation",
        "artifact_families": archive_families,
        "family_count": len(archive_families),
        "path_count": sum(len(family["paths"]) for family in archive_families),
        "expected_validation_commands": list(EXPECTED_LEVEL18_COMMANDS),
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }
    validate_level18_archive_index(index)
    return index


def validate_level18_archive_index(index: dict[str, Any]) -> None:
    """Validate Level 18 archive-index shape."""

    if not isinstance(index, dict):
        raise Level18ArchiveIndexError("index must be an object")
    _eq(index.get("format"), LEVEL18_ARCHIVE_INDEX_FORMAT, "index.format")
    _eq(index.get("phase"), LEVEL18_ARCHIVE_INDEX_PHASE, "index.phase")
    _non_empty(index.get("reviewer"), "index.reviewer")
    _non_empty(index.get("reviewed_at"), "index.reviewed_at")
    _eq(index.get("archive_status"), "pending_local_validation", "index.archive_status")
    families = index.get("artifact_families")
    if not isinstance(families, list) or not families:
        raise Level18ArchiveIndexError("index.artifact_families must be a non-empty list")
    seen: set[str] = set()
    path_count = 0
    for family in families:
        if not isinstance(family, dict):
            raise Level18ArchiveIndexError("index.artifact_families[] must be an object")
        name = _non_empty(family.get("family"), "family.family")
        if name in seen:
            raise Level18ArchiveIndexError(f"duplicate family: {name}")
        seen.add(name)
        paths = family.get("paths")
        if not isinstance(paths, list) or not paths:
            raise Level18ArchiveIndexError(f"family {name} paths must be a non-empty list")
        for path in paths:
            _validate_relative_report_path(path)
        path_count += len(paths)
    _eq(index.get("family_count"), len(families), "index.family_count")
    _eq(index.get("path_count"), path_count, "index.path_count")
    _eq(
        index.get("expected_validation_commands"),
        EXPECTED_LEVEL18_COMMANDS,
        "index.expected_validation_commands",
    )
    flags = index.get("flags")
    if not isinstance(flags, dict):
        raise Level18ArchiveIndexError("index.flags must be an object")
    _eq(flags.get("review_only"), True, "index.flags.review_only")
    _eq(flags.get("path_only"), True, "index.flags.path_only")
    for key in ["content_read", "command_executed", "claim_generated"]:
        _eq(flags.get(key), False, f"index.flags.{key}")


def render_level18_archive_index_report(index: dict[str, Any]) -> str:
    """Render a Markdown report for Level 18 archive index."""

    validate_level18_archive_index(index)
    lines = [
        "# Level 18 Archive Index Report",
        "",
        f"- Phase: `{LEVEL18_ARCHIVE_INDEX_REPORT_PHASE}`",
        f"- Archive status: `{index['archive_status']}`",
        f"- Family count: `{index['family_count']}`",
        f"- Path count: `{index['path_count']}`",
        "",
        "## Artifact families",
        "",
    ]
    for family in index["artifact_families"]:
        lines.append(f"### `{family['family']}`")
        lines.append("")
        for path in family["paths"]:
            lines.append(f"- `{path}`")
        lines.append("")
    lines.extend(["## Path-only inventory", "", "Path only: `True`", ""])
    lines.extend(
        [
            "## Review-only boundary",
            "",
            "Review only: `True`",
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
            "- Focused Level 18 tests must pass locally.",
            "- `ruff check .` must pass locally.",
            "- Full `pytest` must pass locally.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level18_archive_index_report(markdown)
    return markdown


def validate_level18_archive_index_report(markdown: str) -> None:
    """Validate Level 18 archive-index Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level18ArchiveIndexError("markdown must be a newline-terminated string")
    for text in [
        "# Level 18 Archive Index Report",
        "## Artifact families",
        "## Path-only inventory",
        "## Review-only boundary",
        "## Expected validation commands",
        "## Next-level preconditions",
        "Path only: `True`",
        "Review only: `True`",
        "Content read: `False`",
        "Command executed: `False`",
        "Claim generated: `False`",
    ]:
        if text not in markdown:
            raise Level18ArchiveIndexError(f"missing markdown text: {text}")


def write_level18_archive_index(path: Path, index: dict[str, Any]) -> None:
    """Write Level 18 archive index JSON."""

    validate_level18_archive_index(index)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level18_archive_index_report(path: Path, markdown: str) -> None:
    """Write Level 18 archive-index Markdown report."""

    validate_level18_archive_index_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _copy_families(families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "family": str(family.get("family", "")),
            "paths": [str(path) for path in family.get("paths", [])],
        }
        for family in families
    ]


def _validate_relative_report_path(value: Any) -> str:
    path = _non_empty(value, "path")
    parsed = PurePosixPath(path.replace("\\", "/"))
    if parsed.is_absolute():
        raise Level18ArchiveIndexError("path must be relative")
    if ".." in parsed.parts:
        raise Level18ArchiveIndexError("path must not contain parent-directory segments")
    if len(parsed.parts) < 3 or parsed.parts[:2] != ("reports", "local"):
        raise Level18ArchiveIndexError("path must stay under reports/local")
    return path


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level18ArchiveIndexError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level18ArchiveIndexError(f"{name} must be {expected!r}")
