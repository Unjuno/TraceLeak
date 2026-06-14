"""Local file index helpers for metadata demo outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

METADATA_DEMO_ARTIFACT_INDEX_FORMAT = "traceleak.metadata_demo_artifact_index.v1"
METADATA_DEMO_ARTIFACT_INDEX_PHASE = "P76"
DEFAULT_ARTIFACT_ROLES = {
    "sample-contract.json": "sample contract",
    "sample-manifest.json": "sample manifest",
    "approval-record.json": "approval record",
    "approval-gate.json": "approval gate",
    "request-contract.json": "request contract",
    "output-contract.json": "output contract",
    "output-manifest.json": "output manifest",
    "metadata-sample.json": "metadata sample",
    "model-preflight.json": "model preflight",
    "demo-summary.json": "demo summary",
    "baseline-result.json": "baseline result",
    "nn-result.json": "neural model result",
    "demo-manifest.json": "demo manifest",
    "demo-summary.md": "markdown summary",
    "demo-metrics.json": "compact metrics json",
    "demo-metrics.csv": "compact metrics csv",
}


class MetadataDemoArtifactIndexError(ValueError):
    """Raised when a metadata demo artifact index is invalid."""


def build_metadata_demo_artifact_index(
    *,
    output_dir: Path,
    expected_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a filename-only index for local metadata demo outputs."""

    roles = dict(DEFAULT_ARTIFACT_ROLES if expected_files is None else expected_files)
    if not roles:
        raise MetadataDemoArtifactIndexError("expected_files must not be empty")
    files = []
    for filename, role in sorted(roles.items()):
        _safe_filename(filename)
        if not isinstance(role, str) or not role:
            raise MetadataDemoArtifactIndexError("role must be a non-empty string")
        path = output_dir / filename
        files.append(
            {
                "filename": filename,
                "role": role,
                "exists": path.is_file(),
                "size_bytes": path.stat().st_size if path.is_file() else None,
            }
        )
    index = {
        "format": METADATA_DEMO_ARTIFACT_INDEX_FORMAT,
        "phase": METADATA_DEMO_ARTIFACT_INDEX_PHASE,
        "output_dir_name": output_dir.name,
        "file_count": len(files),
        "present_count": sum(1 for item in files if item["exists"]),
        "missing_count": sum(1 for item in files if not item["exists"]),
        "files": files,
        "payload_inspected": False,
    }
    validate_metadata_demo_artifact_index(index)
    return index


def render_metadata_demo_artifact_index_markdown(index: dict[str, Any]) -> str:
    """Render the local artifact index as a compact Markdown table."""

    validate_metadata_demo_artifact_index(index)
    lines = [
        "# Metadata Demo Artifact Index",
        "",
        f"- Present files: `{index['present_count']}`",
        f"- Missing files: `{index['missing_count']}`",
        "- Payload inspected: `False`",
        "",
        "| File | Role | Status | Size bytes |",
        "|---|---|---:|---:|",
    ]
    for item in index["files"]:
        status = "present" if item["exists"] else "missing"
        size = "" if item["size_bytes"] is None else str(item["size_bytes"])
        lines.append(f"| `{item['filename']}` | {item['role']} | {status} | {size} |")
    lines.append("")
    markdown = "\n".join(lines)
    validate_metadata_demo_artifact_index_markdown(markdown)
    return markdown


def write_metadata_demo_artifact_index_json(path: Path, index: dict[str, Any]) -> None:
    """Write local artifact index JSON."""

    validate_metadata_demo_artifact_index(index)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_metadata_demo_artifact_index_markdown(path: Path, markdown: str) -> None:
    """Write local artifact index Markdown."""

    validate_metadata_demo_artifact_index_markdown(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def validate_metadata_demo_artifact_index(index: dict[str, Any]) -> None:
    """Validate a local metadata demo artifact index."""

    _eq(index.get("format"), METADATA_DEMO_ARTIFACT_INDEX_FORMAT, "index.format")
    _eq(index.get("phase"), METADATA_DEMO_ARTIFACT_INDEX_PHASE, "index.phase")
    if not isinstance(index.get("output_dir_name"), str) or not index["output_dir_name"]:
        raise MetadataDemoArtifactIndexError("index.output_dir_name must be a non-empty string")
    files = index.get("files")
    if not isinstance(files, list) or not files:
        raise MetadataDemoArtifactIndexError("index.files must be a non-empty list")
    present_count = 0
    missing_count = 0
    for item in files:
        if not isinstance(item, dict):
            raise MetadataDemoArtifactIndexError("index.files entries must be objects")
        _safe_filename(item.get("filename"))
        if not isinstance(item.get("role"), str) or not item["role"]:
            raise MetadataDemoArtifactIndexError("index.files role must be a non-empty string")
        if item.get("exists") is True:
            present_count += 1
            if not isinstance(item.get("size_bytes"), int) or item["size_bytes"] < 0:
                raise MetadataDemoArtifactIndexError("present file size_bytes must be non-negative")
        elif item.get("exists") is False:
            missing_count += 1
            if item.get("size_bytes") is not None:
                raise MetadataDemoArtifactIndexError("missing file size_bytes must be null")
        else:
            raise MetadataDemoArtifactIndexError("index.files exists must be boolean")
    _eq(index.get("file_count"), len(files), "index.file_count")
    _eq(index.get("present_count"), present_count, "index.present_count")
    _eq(index.get("missing_count"), missing_count, "index.missing_count")
    _eq(index.get("payload_inspected"), False, "index.payload_inspected")


def validate_metadata_demo_artifact_index_markdown(markdown: str) -> None:
    """Validate the artifact index Markdown shape."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise MetadataDemoArtifactIndexError("markdown must be a newline-terminated string")
    for text in [
        "# Metadata Demo Artifact Index",
        "| File | Role | Status | Size bytes |",
        "- Payload inspected: `False`",
    ]:
        if text not in markdown:
            raise MetadataDemoArtifactIndexError(f"missing markdown text: {text}")


def _safe_filename(value: Any) -> None:
    if not isinstance(value, str) or not value:
        raise MetadataDemoArtifactIndexError("filename must be a non-empty string")
    path = Path(value)
    if path.name != value or path.is_absolute() or ".." in path.parts:
        raise MetadataDemoArtifactIndexError("filename must be a plain relative file name")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise MetadataDemoArtifactIndexError(f"{name} must be {expected!r}")
