"""Path-only Level 8 intake for approved local metadata/report artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level7_review_gate import (
    ACCEPTED_LEVEL7_ARTIFACT_CLASSES,
    LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT,
    REJECTED_LEVEL7_ARTIFACT_CLASSES,
    validate_level7_artifact_boundary_plan,
)

LEVEL8_ARTIFACT_INTAKE_MANIFEST_FORMAT = "traceleak.level8_artifact_intake_manifest.v1"
LEVEL8_ARTIFACT_INTAKE_MANIFEST_PHASE = "P114"
LEVEL8_ARTIFACT_INTAKE_INDEX_FORMAT = "traceleak.level8_artifact_intake_index.v1"
LEVEL8_ARTIFACT_INTAKE_INDEX_PHASE = "P116"
LEVEL8_ARTIFACT_INTAKE_REPORT_PHASE = "P117"
DEFAULT_LEVEL8_ARTIFACTS = [
    {
        "key": "level6_profile_input",
        "artifact_class": "profile_json",
        "relative_path": "reports/local/level6_profile/profile-input.json",
        "role": "Level 6 profile input",
    },
    {
        "key": "level6_adapter_input",
        "artifact_class": "adapter_input_json",
        "relative_path": "reports/local/level6_profile/adapter-input.json",
        "role": "Level 6 adapter input",
    },
    {
        "key": "level6_model_sequence",
        "artifact_class": "model_sequence_json",
        "relative_path": "reports/local/level6_profile/profile-model-sequence.json",
        "role": "Level 6 model-sequence sample",
    },
    {
        "key": "level6_baseline_result",
        "artifact_class": "baseline_result_json",
        "relative_path": "reports/local/level6_profile/profile-baseline-result.json",
        "role": "Level 6 baseline result",
    },
    {
        "key": "level6_nn_result",
        "artifact_class": "nn_result_json",
        "relative_path": "reports/local/level6_profile/profile-nn-result.json",
        "role": "Level 6 NN result",
    },
    {
        "key": "level6_summary",
        "artifact_class": "summary_json",
        "relative_path": "reports/local/level6_profile/profile-demo-summary.json",
        "role": "Level 6 profile summary",
    },
    {
        "key": "level6_report",
        "artifact_class": "markdown_report",
        "relative_path": "reports/local/level6_profile/profile-demo-report.md",
        "role": "Level 6 profile report",
    },
    {
        "key": "level7_readiness",
        "artifact_class": "markdown_report",
        "relative_path": "reports/local/level7_planning/level7-readiness-report.md",
        "role": "Level 7 readiness report",
    },
]


class Level8ArtifactIntakeError(ValueError):
    """Raised when Level 8 artifact intake data is invalid."""


def build_level8_artifact_intake_manifest(
    *,
    artifact_boundary_plan: dict[str, Any],
    entries: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a path-only intake manifest for approved metadata/report artifacts."""

    validate_level7_artifact_boundary_plan(artifact_boundary_plan)
    manifest = {
        "format": LEVEL8_ARTIFACT_INTAKE_MANIFEST_FORMAT,
        "phase": LEVEL8_ARTIFACT_INTAKE_MANIFEST_PHASE,
        "boundary_plan_format": artifact_boundary_plan["format"],
        "boundary_plan_phase": artifact_boundary_plan["phase"],
        "accepted_artifact_classes": artifact_boundary_plan["accepted_artifact_classes"],
        "rejected_artifact_classes": artifact_boundary_plan["rejected_artifact_classes"],
        "entries": [dict(item) for item in (entries or DEFAULT_LEVEL8_ARTIFACTS)],
        "payload_reading_allowed": False,
        "claim_generation_allowed": False,
    }
    validate_level8_artifact_intake_manifest(manifest)
    return manifest


def validate_level8_artifact_intake_manifest(manifest: dict[str, Any]) -> None:
    """Validate a Level 8 path-only artifact intake manifest."""

    if not isinstance(manifest, dict):
        raise Level8ArtifactIntakeError("manifest must be an object")
    _eq(manifest.get("format"), LEVEL8_ARTIFACT_INTAKE_MANIFEST_FORMAT, "manifest.format")
    _eq(manifest.get("phase"), LEVEL8_ARTIFACT_INTAKE_MANIFEST_PHASE, "manifest.phase")
    _eq(
        manifest.get("boundary_plan_format"),
        LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT,
        "manifest.boundary_plan_format",
    )
    _eq(
        manifest.get("accepted_artifact_classes"),
        sorted(ACCEPTED_LEVEL7_ARTIFACT_CLASSES),
        "manifest.accepted_artifact_classes",
    )
    _eq(
        manifest.get("rejected_artifact_classes"),
        sorted(REJECTED_LEVEL7_ARTIFACT_CLASSES),
        "manifest.rejected_artifact_classes",
    )
    _eq(manifest.get("payload_reading_allowed"), False, "manifest.payload_reading_allowed")
    _eq(manifest.get("claim_generation_allowed"), False, "manifest.claim_generation_allowed")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise Level8ArtifactIntakeError("manifest.entries must be a non-empty list")
    seen_keys: set[str] = set()
    accepted = set(manifest["accepted_artifact_classes"])
    rejected = set(manifest["rejected_artifact_classes"])
    for index, entry in enumerate(entries):
        _validate_manifest_entry(entry, index, seen_keys, accepted, rejected)


def build_level8_artifact_intake_index(
    *,
    manifest: dict[str, Any],
    root_dir: Path = Path("."),
) -> dict[str, Any]:
    """Build a file-stat-only index from a Level 8 intake manifest."""

    validate_level8_artifact_intake_manifest(manifest)
    indexed_entries = []
    for entry in manifest["entries"]:
        path = root_dir / entry["relative_path"]
        exists = path.is_file()
        indexed_entries.append(
            {
                "key": entry["key"],
                "artifact_class": entry["artifact_class"],
                "relative_path": entry["relative_path"],
                "role": entry["role"],
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else None,
            }
        )
    index = {
        "format": LEVEL8_ARTIFACT_INTAKE_INDEX_FORMAT,
        "phase": LEVEL8_ARTIFACT_INTAKE_INDEX_PHASE,
        "manifest_format": manifest["format"],
        "entry_count": len(indexed_entries),
        "present_count": sum(1 for item in indexed_entries if item["exists"]),
        "missing_count": sum(1 for item in indexed_entries if not item["exists"]),
        "entries": indexed_entries,
        "payload_read": False,
        "claim_generated": False,
    }
    validate_level8_artifact_intake_index(index)
    return index


def validate_level8_artifact_intake_index(index: dict[str, Any]) -> None:
    """Validate a Level 8 path-only artifact intake index."""

    if not isinstance(index, dict):
        raise Level8ArtifactIntakeError("index must be an object")
    _eq(index.get("format"), LEVEL8_ARTIFACT_INTAKE_INDEX_FORMAT, "index.format")
    _eq(index.get("phase"), LEVEL8_ARTIFACT_INTAKE_INDEX_PHASE, "index.phase")
    _eq(index.get("manifest_format"), LEVEL8_ARTIFACT_INTAKE_MANIFEST_FORMAT, "index.manifest_format")
    entries = index.get("entries")
    if not isinstance(entries, list) or not entries:
        raise Level8ArtifactIntakeError("index.entries must be a non-empty list")
    present_count = 0
    missing_count = 0
    seen_keys: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise Level8ArtifactIntakeError("index entries must be objects")
        key = _non_empty(entry.get("key"), "index.entry.key")
        if key in seen_keys:
            raise Level8ArtifactIntakeError("index entry keys must be unique")
        seen_keys.add(key)
        _validate_artifact_class(entry.get("artifact_class"))
        _safe_local_path(entry.get("relative_path"), "index.entry.relative_path")
        _non_empty(entry.get("role"), "index.entry.role")
        if entry.get("exists") is True:
            present_count += 1
            if not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] < 0:
                raise Level8ArtifactIntakeError("present size_bytes must be non-negative")
        elif entry.get("exists") is False:
            missing_count += 1
            if entry.get("size_bytes") is not None:
                raise Level8ArtifactIntakeError("missing size_bytes must be null")
        else:
            raise Level8ArtifactIntakeError("entry.exists must be boolean")
    _eq(index.get("entry_count"), len(entries), "index.entry_count")
    _eq(index.get("present_count"), present_count, "index.present_count")
    _eq(index.get("missing_count"), missing_count, "index.missing_count")
    _eq(index.get("payload_read"), False, "index.payload_read")
    _eq(index.get("claim_generated"), False, "index.claim_generated")


def render_level8_artifact_intake_report(
    *,
    manifest: dict[str, Any],
    index: dict[str, Any],
) -> str:
    """Render a Markdown report for Level 8 artifact intake."""

    validate_level8_artifact_intake_manifest(manifest)
    validate_level8_artifact_intake_index(index)
    lines = [
        "# Level 8 Artifact Intake Report",
        "",
        f"- Phase: `{LEVEL8_ARTIFACT_INTAKE_REPORT_PHASE}`",
        f"- Manifest format: `{manifest['format']}`",
        f"- Index format: `{index['format']}`",
        f"- Entries: `{index['entry_count']}`",
        f"- Present: `{index['present_count']}`",
        f"- Missing: `{index['missing_count']}`",
        "",
        "## Intake manifest status",
        "",
        f"- Payload reading allowed: `{manifest['payload_reading_allowed']}`",
        f"- Claim generation allowed: `{manifest['claim_generation_allowed']}`",
        "",
        "## Accepted artifact classes",
        "",
    ]
    for artifact_class in manifest["accepted_artifact_classes"]:
        lines.append(f"- `{artifact_class}`")
    lines.extend(["", "## Rejected artifact classes", ""])
    for artifact_class in manifest["rejected_artifact_classes"]:
        lines.append(f"- `{artifact_class}`")
    lines.extend(["", "## Present artifacts", ""])
    for entry in index["entries"]:
        if entry["exists"]:
            lines.append(f"- `{entry['key']}`: `{entry['relative_path']}`")
    lines.extend(["", "## Missing artifacts", ""])
    for entry in index["entries"]:
        if not entry["exists"]:
            lines.append(f"- `{entry['key']}`: `{entry['relative_path']}`")
    lines.extend(
        [
            "",
            "## Safety boundary",
            "",
            "Payload contents were not read.",
            "No claim was generated.",
            "Artifacts remain under `reports/local/`.",
            "",
            "## Local validation commands",
            "",
            "```powershell",
            "pytest tests/test_level8_artifact_intake_manifest.py",
            "pytest tests/test_level8_artifact_intake_index.py",
            "pytest tests/test_level8_artifact_intake_report.py",
            "pytest tests/test_write_level8_artifacts_cli.py",
            "ruff check .",
            "pytest",
            "```",
            "",
        ]
    )
    markdown = "\n".join(lines)
    validate_level8_artifact_intake_report(markdown)
    return markdown


def validate_level8_artifact_intake_report(markdown: str) -> None:
    """Validate Level 8 artifact intake Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level8ArtifactIntakeError("markdown must be a newline-terminated string")
    for text in [
        "# Level 8 Artifact Intake Report",
        "## Intake manifest status",
        "## Accepted artifact classes",
        "## Rejected artifact classes",
        "## Present artifacts",
        "## Missing artifacts",
        "## Safety boundary",
        "Payload contents were not read.",
        "No claim was generated.",
        "Artifacts remain under `reports/local/`.",
    ]:
        if text not in markdown:
            raise Level8ArtifactIntakeError(f"missing markdown text: {text}")


def write_level8_artifact_intake_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Write Level 8 artifact intake manifest JSON."""

    validate_level8_artifact_intake_manifest(manifest)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level8_artifact_intake_index(path: Path, index: dict[str, Any]) -> None:
    """Write Level 8 artifact intake index JSON."""

    validate_level8_artifact_intake_index(index)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level8_artifact_intake_report(path: Path, markdown: str) -> None:
    """Write Level 8 artifact intake report Markdown."""

    validate_level8_artifact_intake_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _validate_manifest_entry(
    entry: Any,
    index: int,
    seen_keys: set[str],
    accepted: set[str],
    rejected: set[str],
) -> None:
    if not isinstance(entry, dict):
        raise Level8ArtifactIntakeError(f"manifest.entries[{index}] must be an object")
    key = _non_empty(entry.get("key"), f"manifest.entries[{index}].key")
    if key in seen_keys:
        raise Level8ArtifactIntakeError("manifest entry keys must be unique")
    seen_keys.add(key)
    artifact_class = _non_empty(entry.get("artifact_class"), f"manifest.entries[{index}].artifact_class")
    if artifact_class in rejected:
        raise Level8ArtifactIntakeError(f"artifact class is rejected: {artifact_class}")
    if artifact_class not in accepted:
        raise Level8ArtifactIntakeError(f"artifact class is not accepted: {artifact_class}")
    _safe_local_path(entry.get("relative_path"), f"manifest.entries[{index}].relative_path")
    _non_empty(entry.get("role"), f"manifest.entries[{index}].role")


def _validate_artifact_class(value: Any) -> str:
    artifact_class = _non_empty(value, "artifact_class")
    if artifact_class in REJECTED_LEVEL7_ARTIFACT_CLASSES:
        raise Level8ArtifactIntakeError(f"artifact class is rejected: {artifact_class}")
    if artifact_class not in ACCEPTED_LEVEL7_ARTIFACT_CLASSES:
        raise Level8ArtifactIntakeError(f"artifact class is not accepted: {artifact_class}")
    return artifact_class


def _safe_local_path(value: Any, name: str) -> str:
    text = _non_empty(value, name)
    normalized = text.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise Level8ArtifactIntakeError(f"{name} must be a safe relative path")
    if path.parts[:2] != ("reports", "local"):
        raise Level8ArtifactIntakeError(f"{name} must be under reports/local")
    return normalized


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level8ArtifactIntakeError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level8ArtifactIntakeError(f"{name} must be {expected!r}")
