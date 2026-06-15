"""Level 13 closure and handoff inventory helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level12_review_checkpoint import (
    LEVEL12_REVIEW_CHECKPOINT_FORMAT,
    validate_level12_review_checkpoint,
)

LEVEL13_CLOSURE_MANIFEST_FORMAT = "traceleak.level13_closure_manifest.v1"
LEVEL13_CLOSURE_MANIFEST_PHASE = "P137"
LEVEL13_HANDOFF_INVENTORY_FORMAT = "traceleak.level13_handoff_inventory.v1"
LEVEL13_HANDOFF_INVENTORY_PHASE = "P138"
LEVEL13_CLOSURE_REPORT_PHASE = "P139"
DEFAULT_HANDOFF_FAMILIES = [
    {
        "family": "level6_profile",
        "role": "profile demo artifacts",
        "paths": [
            "reports/local/level6_profile/profile-input.json",
            "reports/local/level6_profile/adapter-input.json",
            "reports/local/level6_profile/profile-demo-summary.json",
            "reports/local/level6_profile/profile-demo-report.md",
        ],
    },
    {
        "family": "level7_planning",
        "role": "planning artifacts",
        "paths": [
            "reports/local/level7_planning/level7-review-gate.json",
            "reports/local/level7_planning/level7-planning-contract.json",
            "reports/local/level7_planning/level7-readiness-report.md",
        ],
    },
    {
        "family": "level8_intake",
        "role": "path-only intake artifacts",
        "paths": [
            "reports/local/level8_intake/level8-manifest.json",
            "reports/local/level8_intake/level8-index.json",
            "reports/local/level8_intake/level8-report.md",
        ],
    },
    {
        "family": "level9_readiness",
        "role": "readiness artifacts",
        "paths": [
            "reports/local/level9_readiness/level9-readiness-audit.json",
            "reports/local/level9_readiness/level9-readiness-report.md",
        ],
    },
    {
        "family": "level10_review",
        "role": "review packet artifacts",
        "paths": [
            "reports/local/level10_review/level10-review-packet.json",
            "reports/local/level10_review/level10-review-packet.md",
        ],
    },
    {
        "family": "level11_next_todo",
        "role": "next TODO proposal artifacts",
        "paths": [
            "reports/local/level11_next_todo/level11-next-todo-proposal.json",
            "reports/local/level11_next_todo/level11-next-todo-proposal.md",
        ],
    },
    {
        "family": "level12_checkpoint",
        "role": "review checkpoint artifacts",
        "paths": [
            "reports/local/level12_checkpoint/level12-review-checkpoint.json",
            "reports/local/level12_checkpoint/level12-review-checkpoint.md",
        ],
    },
]


class Level13ClosureError(ValueError):
    """Raised when Level 13 closure data is invalid."""


def build_level13_closure_manifest(
    *,
    review_checkpoint: dict[str, Any],
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a Level 13 closure manifest from a Level 12 checkpoint."""

    validate_level12_review_checkpoint(review_checkpoint)
    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    ready = review_checkpoint["checkpoint_status"] == "ready_for_level12_todo"
    manifest = {
        "format": LEVEL13_CLOSURE_MANIFEST_FORMAT,
        "phase": LEVEL13_CLOSURE_MANIFEST_PHASE,
        "source_checkpoint_format": review_checkpoint["format"],
        "source_checkpoint_phase": review_checkpoint["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "checkpoint_status": review_checkpoint["checkpoint_status"],
        "closure_status": "ready_for_handoff" if ready else "blocked_by_checkpoint",
        "required_preconditions": dict(review_checkpoint["required_preconditions"]),
        "allowances": {
            "closure_only": True,
            "direct_action_enabled": False,
            "content_read_enabled": False,
            "claim_enabled": False,
        },
    }
    validate_level13_closure_manifest(manifest)
    return manifest


def validate_level13_closure_manifest(manifest: dict[str, Any]) -> None:
    """Validate Level 13 closure manifest shape."""

    if not isinstance(manifest, dict):
        raise Level13ClosureError("manifest must be an object")
    _eq(manifest.get("format"), LEVEL13_CLOSURE_MANIFEST_FORMAT, "manifest.format")
    _eq(manifest.get("phase"), LEVEL13_CLOSURE_MANIFEST_PHASE, "manifest.phase")
    _eq(
        manifest.get("source_checkpoint_format"),
        LEVEL12_REVIEW_CHECKPOINT_FORMAT,
        "manifest.source_checkpoint_format",
    )
    _non_empty(manifest.get("reviewer"), "manifest.reviewer")
    _non_empty(manifest.get("reviewed_at"), "manifest.reviewed_at")
    if manifest.get("checkpoint_status") not in {
        "ready_for_level12_todo",
        "blocked_by_level11_proposal",
    }:
        raise Level13ClosureError("manifest.checkpoint_status is invalid")
    expected_status = (
        "ready_for_handoff"
        if manifest["checkpoint_status"] == "ready_for_level12_todo"
        else "blocked_by_checkpoint"
    )
    _eq(manifest.get("closure_status"), expected_status, "manifest.closure_status")
    preconditions = manifest.get("required_preconditions")
    if not isinstance(preconditions, dict):
        raise Level13ClosureError("manifest.required_preconditions must be an object")
    for key in ["focused_tests_passed", "ruff_passed", "full_pytest_passed"]:
        _eq(preconditions.get(key), False, f"manifest.required_preconditions.{key}")
    _eq(preconditions.get("new_review_recorded"), True, "manifest.required_preconditions.new_review_recorded")
    allowances = manifest.get("allowances")
    if not isinstance(allowances, dict):
        raise Level13ClosureError("manifest.allowances must be an object")
    _eq(allowances.get("closure_only"), True, "manifest.allowances.closure_only")
    for key in ["direct_action_enabled", "content_read_enabled", "claim_enabled"]:
        _eq(allowances.get(key), False, f"manifest.allowances.{key}")


def build_level13_handoff_inventory(
    *,
    closure_manifest: dict[str, Any],
    families: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a path-only Level 13 handoff inventory."""

    validate_level13_closure_manifest(closure_manifest)
    inventory = {
        "format": LEVEL13_HANDOFF_INVENTORY_FORMAT,
        "phase": LEVEL13_HANDOFF_INVENTORY_PHASE,
        "closure_manifest_format": closure_manifest["format"],
        "closure_manifest_phase": closure_manifest["phase"],
        "closure_status": closure_manifest["closure_status"],
        "families": [dict(item) for item in (families or DEFAULT_HANDOFF_FAMILIES)],
        "flags": {
            "path_only": True,
            "content_read": False,
            "claim_generated": False,
        },
    }
    validate_level13_handoff_inventory(inventory)
    return inventory


def validate_level13_handoff_inventory(inventory: dict[str, Any]) -> None:
    """Validate Level 13 handoff inventory shape."""

    if not isinstance(inventory, dict):
        raise Level13ClosureError("inventory must be an object")
    _eq(inventory.get("format"), LEVEL13_HANDOFF_INVENTORY_FORMAT, "inventory.format")
    _eq(inventory.get("phase"), LEVEL13_HANDOFF_INVENTORY_PHASE, "inventory.phase")
    _eq(
        inventory.get("closure_manifest_format"),
        LEVEL13_CLOSURE_MANIFEST_FORMAT,
        "inventory.closure_manifest_format",
    )
    if inventory.get("closure_status") not in {"ready_for_handoff", "blocked_by_checkpoint"}:
        raise Level13ClosureError("inventory.closure_status is invalid")
    families = inventory.get("families")
    if not isinstance(families, list) or not families:
        raise Level13ClosureError("inventory.families must be a non-empty list")
    seen: set[str] = set()
    for index, family in enumerate(families):
        if not isinstance(family, dict):
            raise Level13ClosureError(f"inventory.families[{index}] must be an object")
        name = _non_empty(family.get("family"), f"inventory.families[{index}].family")
        if name in seen:
            raise Level13ClosureError("inventory family names must be unique")
        seen.add(name)
        _non_empty(family.get("role"), f"inventory.families[{index}].role")
        paths = family.get("paths")
        if not isinstance(paths, list) or not paths:
            raise Level13ClosureError(f"inventory.families[{index}].paths must be a non-empty list")
        for path_index, path in enumerate(paths):
            _safe_report_path(path, f"inventory.families[{index}].paths[{path_index}]")
    flags = inventory.get("flags")
    if not isinstance(flags, dict):
        raise Level13ClosureError("inventory.flags must be an object")
    _eq(flags.get("path_only"), True, "inventory.flags.path_only")
    _eq(flags.get("content_read"), False, "inventory.flags.content_read")
    _eq(flags.get("claim_generated"), False, "inventory.flags.claim_generated")


def render_level13_closure_report(
    *,
    closure_manifest: dict[str, Any],
    handoff_inventory: dict[str, Any],
) -> str:
    """Render a Markdown report for Level 13 closure."""

    validate_level13_closure_manifest(closure_manifest)
    validate_level13_handoff_inventory(handoff_inventory)
    lines = [
        "# Level 13 Closure Report",
        "",
        f"- Phase: `{LEVEL13_CLOSURE_REPORT_PHASE}`",
        f"- Closure status: `{closure_manifest['closure_status']}`",
        f"- Checkpoint status: `{closure_manifest['checkpoint_status']}`",
        "",
        "## Required preconditions",
        "",
        f"- Focused tests passed: `{closure_manifest['required_preconditions']['focused_tests_passed']}`",
        f"- Ruff passed: `{closure_manifest['required_preconditions']['ruff_passed']}`",
        f"- Full pytest passed: `{closure_manifest['required_preconditions']['full_pytest_passed']}`",
        f"- New review recorded: `{closure_manifest['required_preconditions']['new_review_recorded']}`",
        "",
        "## Handoff inventory summary",
        "",
    ]
    for family in handoff_inventory["families"]:
        lines.append(f"- `{family['family']}`: `{len(family['paths'])}` paths")
    lines.extend(
        [
            "",
            "## Review-only boundary",
            "",
            "Closure only: `True`",
            "Path-only inventory: `True`",
            "Content read: `False`",
            "Claim generated: `False`",
            "",
            "## Local validation commands",
            "",
            "```powershell",
            "pytest tests/test_level13_closure_manifest.py",
            "pytest tests/test_level13_handoff_inventory.py",
            "pytest tests/test_level13_closure_report.py",
            "pytest tests/test_write_level13_files_cli.py",
            "ruff check .",
            "pytest",
            "```",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level13_closure_report(markdown)
    return markdown


def validate_level13_closure_report(markdown: str) -> None:
    """Validate Level 13 closure Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level13ClosureError("markdown must be a newline-terminated string")
    for text in [
        "# Level 13 Closure Report",
        "## Required preconditions",
        "## Handoff inventory summary",
        "## Review-only boundary",
        "Closure only: `True`",
        "Path-only inventory: `True`",
        "Content read: `False`",
        "Claim generated: `False`",
    ]:
        if text not in markdown:
            raise Level13ClosureError(f"missing markdown text: {text}")


def write_level13_closure_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Write Level 13 closure manifest JSON."""

    validate_level13_closure_manifest(manifest)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level13_handoff_inventory(path: Path, inventory: dict[str, Any]) -> None:
    """Write Level 13 handoff inventory JSON."""

    validate_level13_handoff_inventory(inventory)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level13_closure_report(path: Path, markdown: str) -> None:
    """Write Level 13 closure Markdown report."""

    validate_level13_closure_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _safe_report_path(value: Any, name: str) -> str:
    text = _non_empty(value, name)
    path = Path(text.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise Level13ClosureError(f"{name} must be a safe relative path")
    if path.parts[:2] != ("reports", "local"):
        raise Level13ClosureError(f"{name} must be under reports/local")
    return text


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level13ClosureError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level13ClosureError(f"{name} must be {expected!r}")
