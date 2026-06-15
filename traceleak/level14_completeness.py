"""Level 14 handoff completeness audit helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level13_closure import (
    LEVEL13_HANDOFF_INVENTORY_FORMAT,
    validate_level13_handoff_inventory,
)

LEVEL14_COMPLETENESS_AUDIT_FORMAT = "traceleak.level14_completeness_audit.v1"
LEVEL14_COMPLETENESS_AUDIT_PHASE = "P143"
LEVEL14_COMPLETENESS_REPORT_PHASE = "P144"
REQUIRED_HANDOFF_FAMILIES = [
    "level6_profile",
    "level7_planning",
    "level8_intake",
    "level9_readiness",
    "level10_review",
    "level11_next_todo",
    "level12_checkpoint",
]


class Level14CompletenessError(ValueError):
    """Raised when Level 14 completeness data is invalid."""


def build_level14_completeness_audit(*, handoff_inventory: dict[str, Any]) -> dict[str, Any]:
    """Build a path-only completeness audit from a Level 13 handoff inventory."""

    validate_level13_handoff_inventory(handoff_inventory)
    families = handoff_inventory["families"]
    family_names = [family["family"] for family in families]
    missing = [name for name in REQUIRED_HANDOFF_FAMILIES if name not in family_names]
    total_path_count = sum(len(family["paths"]) for family in families)
    audit = {
        "format": LEVEL14_COMPLETENESS_AUDIT_FORMAT,
        "phase": LEVEL14_COMPLETENESS_AUDIT_PHASE,
        "source_inventory_format": handoff_inventory["format"],
        "source_inventory_phase": handoff_inventory["phase"],
        "required_families": list(REQUIRED_HANDOFF_FAMILIES),
        "observed_families": family_names,
        "family_count": len(families),
        "path_count": total_path_count,
        "missing_required_families": missing,
        "completeness_status": "complete" if not missing else "incomplete",
        "flags": {
            "path_only": True,
            "content_read": False,
            "claim_generated": False,
        },
    }
    validate_level14_completeness_audit(audit)
    return audit


def validate_level14_completeness_audit(audit: dict[str, Any]) -> None:
    """Validate Level 14 completeness audit shape."""

    if not isinstance(audit, dict):
        raise Level14CompletenessError("audit must be an object")
    _eq(audit.get("format"), LEVEL14_COMPLETENESS_AUDIT_FORMAT, "audit.format")
    _eq(audit.get("phase"), LEVEL14_COMPLETENESS_AUDIT_PHASE, "audit.phase")
    _eq(
        audit.get("source_inventory_format"),
        LEVEL13_HANDOFF_INVENTORY_FORMAT,
        "audit.source_inventory_format",
    )
    _eq(audit.get("required_families"), REQUIRED_HANDOFF_FAMILIES, "audit.required_families")
    observed = audit.get("observed_families")
    if not isinstance(observed, list) or not observed:
        raise Level14CompletenessError("audit.observed_families must be a non-empty list")
    for name in observed:
        _non_empty(name, "audit.observed_families[]")
    if not isinstance(audit.get("family_count"), int) or audit["family_count"] < 0:
        raise Level14CompletenessError("audit.family_count must be a non-negative integer")
    _eq(audit["family_count"], len(observed), "audit.family_count")
    if not isinstance(audit.get("path_count"), int) or audit["path_count"] < 0:
        raise Level14CompletenessError("audit.path_count must be a non-negative integer")
    missing = audit.get("missing_required_families")
    if not isinstance(missing, list):
        raise Level14CompletenessError("audit.missing_required_families must be a list")
    expected_missing = [name for name in REQUIRED_HANDOFF_FAMILIES if name not in observed]
    _eq(missing, expected_missing, "audit.missing_required_families")
    expected_status = "complete" if not missing else "incomplete"
    _eq(audit.get("completeness_status"), expected_status, "audit.completeness_status")
    flags = audit.get("flags")
    if not isinstance(flags, dict):
        raise Level14CompletenessError("audit.flags must be an object")
    _eq(flags.get("path_only"), True, "audit.flags.path_only")
    _eq(flags.get("content_read"), False, "audit.flags.content_read")
    _eq(flags.get("claim_generated"), False, "audit.flags.claim_generated")


def render_level14_completeness_report(audit: dict[str, Any]) -> str:
    """Render a Markdown report for Level 14 handoff completeness."""

    validate_level14_completeness_audit(audit)
    lines = [
        "# Level 14 Completeness Report",
        "",
        f"- Phase: `{LEVEL14_COMPLETENESS_REPORT_PHASE}`",
        f"- Completeness status: `{audit['completeness_status']}`",
        f"- Family count: `{audit['family_count']}`",
        f"- Path count: `{audit['path_count']}`",
        "",
        "## Required families",
        "",
    ]
    for family in audit["required_families"]:
        lines.append(f"- `{family}`")
    lines.extend(["", "## Missing families", ""])
    if audit["missing_required_families"]:
        for family in audit["missing_required_families"]:
            lines.append(f"- `{family}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Handoff family counts",
            "",
            f"- Observed families: `{len(audit['observed_families'])}`",
            f"- Observed paths: `{audit['path_count']}`",
            "",
            "## Path-only boundary",
            "",
            "Path only: `True`",
            "Content read: `False`",
            "Claim generated: `False`",
            "",
            "## Local validation commands",
            "",
            "```powershell",
            "pytest tests/test_level14_completeness_audit.py",
            "pytest tests/test_level14_completeness_report.py",
            "pytest tests/test_write_level14_files_cli.py",
            "ruff check .",
            "pytest",
            "```",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level14_completeness_report(markdown)
    return markdown


def validate_level14_completeness_report(markdown: str) -> None:
    """Validate Level 14 completeness Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level14CompletenessError("markdown must be a newline-terminated string")
    for text in [
        "# Level 14 Completeness Report",
        "## Required families",
        "## Missing families",
        "## Handoff family counts",
        "## Path-only boundary",
        "Path only: `True`",
        "Content read: `False`",
        "Claim generated: `False`",
    ]:
        if text not in markdown:
            raise Level14CompletenessError(f"missing markdown text: {text}")


def write_level14_completeness_audit(path: Path, audit: dict[str, Any]) -> None:
    """Write Level 14 completeness audit JSON."""

    validate_level14_completeness_audit(audit)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level14_completeness_report(path: Path, markdown: str) -> None:
    """Write Level 14 completeness Markdown report."""

    validate_level14_completeness_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level14CompletenessError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level14CompletenessError(f"{name} must be {expected!r}")
