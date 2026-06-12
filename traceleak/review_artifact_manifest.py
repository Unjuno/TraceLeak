"""Review artifact manifest helpers."""

from __future__ import annotations

from typing import Any

REVIEW_ARTIFACT_MANIFEST_FORMAT = "traceleak.review_artifact_manifest.v1"
REVIEW_ARTIFACT_KINDS = [
    "summary_file",
    "file_index",
    "anchor_report",
    "digest_report",
]


class ReviewArtifactManifestError(ValueError):
    """Raised when a review artifact manifest is invalid."""


def build_review_artifact_manifest(*, stage_plan: dict[str, Any]) -> dict[str, Any]:
    """Build a manifest plan for review artifacts."""

    _require_equal(stage_plan.get("mode"), "review_only", "stage_plan.mode")
    activation = stage_plan.get("activation")
    if not isinstance(activation, dict):
        raise ReviewArtifactManifestError("stage_plan.activation must be an object")
    _require_equal(activation.get("P4"), "planning_only", "stage_plan.activation.P4")
    manifest = {
        "format": REVIEW_ARTIFACT_MANIFEST_FORMAT,
        "status": "ready",
        "mode": "review_only",
        "artifact_kinds": list(REVIEW_ARTIFACT_KINDS),
        "stage": "P4",
        "stage_mode": "planning_only",
    }
    validate_review_artifact_manifest(manifest)
    return manifest


def validate_review_artifact_manifest(manifest: dict[str, Any]) -> None:
    """Validate a review artifact manifest plan."""

    _require_equal(manifest.get("format"), REVIEW_ARTIFACT_MANIFEST_FORMAT, "format")
    _require_equal(manifest.get("status"), "ready", "status")
    _require_equal(manifest.get("mode"), "review_only", "mode")
    _require_equal(manifest.get("stage"), "P4", "stage")
    _require_equal(manifest.get("stage_mode"), "planning_only", "stage_mode")
    kinds = _require_string_list(manifest.get("artifact_kinds"), "artifact_kinds")
    missing = sorted(set(REVIEW_ARTIFACT_KINDS) - set(kinds))
    if missing:
        raise ReviewArtifactManifestError(f"artifact_kinds missing: {', '.join(missing)}")


def _require_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ReviewArtifactManifestError(f"{name} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise ReviewArtifactManifestError(f"{name} must contain only non-empty strings")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise ReviewArtifactManifestError(f"{name} must be {expected!r}")
