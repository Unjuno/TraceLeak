"""Level 9 readiness audit for Level 8 path-only indexes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level8_artifact_intake import (
    LEVEL8_ARTIFACT_INTAKE_INDEX_FORMAT,
    validate_level8_artifact_intake_index,
)

LEVEL9_READINESS_AUDIT_FORMAT = "traceleak.level9_readiness_audit.v1"
LEVEL9_READINESS_AUDIT_PHASE = "P121"
LEVEL9_READINESS_REPORT_PHASE = "P122"


class Level9ReadinessAuditError(ValueError):
    """Raised when Level 9 readiness audit data is invalid."""


def build_level9_readiness_audit(*, intake_index: dict[str, Any]) -> dict[str, Any]:
    """Build a readiness audit from a validated Level 8 path-only index."""

    validate_level8_artifact_intake_index(intake_index)
    entries = intake_index["entries"]
    missing = [
        {
            "key": item["key"],
            "artifact_class": item["artifact_class"],
            "relative_path": item["relative_path"],
            "role": item["role"],
        }
        for item in entries
        if not item["exists"]
    ]
    entry_count = intake_index["entry_count"]
    present_count = intake_index["present_count"]
    readiness_ratio = present_count / entry_count if entry_count else 0.0
    audit = {
        "format": LEVEL9_READINESS_AUDIT_FORMAT,
        "phase": LEVEL9_READINESS_AUDIT_PHASE,
        "source_index_format": intake_index["format"],
        "source_index_phase": intake_index["phase"],
        "entry_count": entry_count,
        "present_count": present_count,
        "missing_count": intake_index["missing_count"],
        "readiness_ratio": readiness_ratio,
        "status": "ready" if not missing else "incomplete",
        "missing_artifacts": missing,
        "flags": {
            "path_only": True,
            "payload_read": False,
            "claim_generated": False,
        },
    }
    validate_level9_readiness_audit(audit)
    return audit


def validate_level9_readiness_audit(audit: dict[str, Any]) -> None:
    """Validate Level 9 readiness audit shape."""

    if not isinstance(audit, dict):
        raise Level9ReadinessAuditError("audit must be an object")
    _eq(audit.get("format"), LEVEL9_READINESS_AUDIT_FORMAT, "audit.format")
    _eq(audit.get("phase"), LEVEL9_READINESS_AUDIT_PHASE, "audit.phase")
    _eq(audit.get("source_index_format"), LEVEL8_ARTIFACT_INTAKE_INDEX_FORMAT, "audit.source_index_format")
    for key in ["entry_count", "present_count", "missing_count"]:
        if not isinstance(audit.get(key), int) or audit[key] < 0:
            raise Level9ReadinessAuditError(f"audit.{key} must be a non-negative integer")
    _eq(audit["present_count"] + audit["missing_count"], audit["entry_count"], "audit.counts")
    ratio = audit.get("readiness_ratio")
    if not isinstance(ratio, int | float) or ratio < 0 or ratio > 1:
        raise Level9ReadinessAuditError("audit.readiness_ratio must be between 0 and 1")
    expected_status = "ready" if audit["missing_count"] == 0 else "incomplete"
    _eq(audit.get("status"), expected_status, "audit.status")
    missing = audit.get("missing_artifacts")
    if not isinstance(missing, list):
        raise Level9ReadinessAuditError("audit.missing_artifacts must be a list")
    _eq(len(missing), audit["missing_count"], "audit.missing_artifacts length")
    for item in missing:
        if not isinstance(item, dict):
            raise Level9ReadinessAuditError("missing artifact entries must be objects")
        _non_empty(item.get("key"), "missing.key")
        _non_empty(item.get("artifact_class"), "missing.artifact_class")
        _safe_report_path(item.get("relative_path"), "missing.relative_path")
        _non_empty(item.get("role"), "missing.role")
    flags = audit.get("flags")
    if not isinstance(flags, dict):
        raise Level9ReadinessAuditError("audit.flags must be an object")
    _eq(flags.get("path_only"), True, "audit.flags.path_only")
    _eq(flags.get("payload_read"), False, "audit.flags.payload_read")
    _eq(flags.get("claim_generated"), False, "audit.flags.claim_generated")


def render_level9_readiness_report(audit: dict[str, Any]) -> str:
    """Render a Markdown report for a Level 9 readiness audit."""

    validate_level9_readiness_audit(audit)
    lines = [
        "# Level 9 Readiness Audit",
        "",
        f"- Phase: `{LEVEL9_READINESS_REPORT_PHASE}`",
        f"- Source index: `{audit['source_index_format']}`",
        f"- Status: `{audit['status']}`",
        f"- Readiness ratio: `{audit['readiness_ratio']}`",
        f"- Entries: `{audit['entry_count']}`",
        f"- Present: `{audit['present_count']}`",
        f"- Missing: `{audit['missing_count']}`",
        "",
        "## Missing artifacts",
        "",
    ]
    if audit["missing_artifacts"]:
        for item in audit["missing_artifacts"]:
            lines.append(f"- `{item['key']}`: `{item['relative_path']}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Path-only: `True`",
            "Payload read: `False`",
            "Claim generated: `False`",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level9_readiness_report(markdown)
    return markdown


def validate_level9_readiness_report(markdown: str) -> None:
    """Validate Level 9 readiness report Markdown."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level9ReadinessAuditError("markdown must be a newline-terminated string")
    for text in [
        "# Level 9 Readiness Audit",
        "## Missing artifacts",
        "## Boundary",
        "Path-only: `True`",
        "Payload read: `False`",
        "Claim generated: `False`",
    ]:
        if text not in markdown:
            raise Level9ReadinessAuditError(f"missing markdown text: {text}")


def write_level9_readiness_audit(path: Path, audit: dict[str, Any]) -> None:
    """Write Level 9 readiness audit JSON."""

    validate_level9_readiness_audit(audit)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level9_readiness_report(path: Path, markdown: str) -> None:
    """Write Level 9 readiness report Markdown."""

    validate_level9_readiness_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _safe_report_path(value: Any, name: str) -> str:
    text = _non_empty(value, name)
    path = Path(text.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise Level9ReadinessAuditError(f"{name} must be a safe relative path")
    if path.parts[:2] != ("reports", "local"):
        raise Level9ReadinessAuditError(f"{name} must be under reports/local")
    return text


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level9ReadinessAuditError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level9ReadinessAuditError(f"{name} must be {expected!r}")
