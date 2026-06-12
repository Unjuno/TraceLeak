"""Review artifact slot set helpers."""

from __future__ import annotations

from typing import Any

from traceleak.review_artifact_manifest import validate_review_artifact_manifest
from traceleak.review_flow_artifact_link import validate_review_flow_artifact_link

REVIEW_ARTIFACT_SLOT_SET_FORMAT = "traceleak.review_artifact_slot_set.v1"


class ReviewArtifactSlotSetError(ValueError):
    """Raised when a review artifact slot set is invalid."""


def build_review_artifact_slot_set(
    *,
    artifact_manifest: dict[str, Any],
    flow_artifact_link: dict[str, Any],
) -> dict[str, Any]:
    """Build planned review artifact slots from a P4 manifest and link."""

    validate_review_artifact_manifest(artifact_manifest)
    validate_review_flow_artifact_link(flow_artifact_link)
    slot_set = {
        "format": REVIEW_ARTIFACT_SLOT_SET_FORMAT,
        "status": "ready",
        "mode": "review_only",
        "stage": "P4",
        "stage_mode": "planning_only",
        "slots": [
            {
                "kind": kind,
                "status": "planned",
                "content_state": "empty",
                "review_required": True,
            }
            for kind in artifact_manifest["artifact_kinds"]
        ],
        "auto_approval": False,
    }
    validate_review_artifact_slot_set(slot_set)
    return slot_set


def validate_review_artifact_slot_set(slot_set: dict[str, Any]) -> None:
    """Validate planned review artifact slots."""

    _require_equal(slot_set.get("format"), REVIEW_ARTIFACT_SLOT_SET_FORMAT, "format")
    _require_equal(slot_set.get("status"), "ready", "status")
    _require_equal(slot_set.get("mode"), "review_only", "mode")
    _require_equal(slot_set.get("stage"), "P4", "stage")
    _require_equal(slot_set.get("stage_mode"), "planning_only", "stage_mode")
    _require_equal(slot_set.get("auto_approval"), False, "auto_approval")
    slots = _require_list(slot_set.get("slots"), "slots")
    for index, slot in enumerate(slots):
        record = _require_dict(slot, f"slots[{index}]")
        _require_string(record.get("kind"), f"slots[{index}].kind")
        _require_equal(record.get("status"), "planned", f"slots[{index}].status")
        _require_equal(record.get("content_state"), "empty", f"slots[{index}].content_state")
        _require_equal(record.get("review_required"), True, f"slots[{index}].review_required")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReviewArtifactSlotSetError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise ReviewArtifactSlotSetError(f"{name} must be a non-empty list")
    return value


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReviewArtifactSlotSetError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise ReviewArtifactSlotSetError(f"{name} must be {expected!r}")
