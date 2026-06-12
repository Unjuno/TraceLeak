"""Link review flow and artifact manifest contracts."""

from __future__ import annotations

from typing import Any

from traceleak.review_artifact_manifest import validate_review_artifact_manifest
from traceleak.review_flow import validate_review_flow

REVIEW_FLOW_ARTIFACT_LINK_FORMAT = "traceleak.review_flow_artifact_link.v1"


class ReviewFlowArtifactLinkError(ValueError):
    """Raised when the review flow artifact link is invalid."""


def build_review_flow_artifact_link(
    *,
    review_flow: dict[str, Any],
    artifact_manifest: dict[str, Any],
) -> dict[str, Any]:
    """Build a P4 link between the review flow and artifact manifest."""

    validate_review_flow(review_flow)
    validate_review_artifact_manifest(artifact_manifest)
    link = {
        "format": REVIEW_FLOW_ARTIFACT_LINK_FORMAT,
        "status": "ready",
        "mode": "review_only",
        "flow_stage": review_flow["stage"],
        "artifact_stage": artifact_manifest["stage"],
        "artifact_stage_mode": artifact_manifest["stage_mode"],
        "auto_approval": False,
    }
    validate_review_flow_artifact_link(link)
    return link


def validate_review_flow_artifact_link(link: dict[str, Any]) -> None:
    """Validate the P4 review flow artifact link."""

    _require_equal(link.get("format"), REVIEW_FLOW_ARTIFACT_LINK_FORMAT, "format")
    _require_equal(link.get("status"), "ready", "status")
    _require_equal(link.get("mode"), "review_only", "mode")
    _require_equal(link.get("flow_stage"), "P3", "flow_stage")
    _require_equal(link.get("artifact_stage"), "P4", "artifact_stage")
    _require_equal(link.get("artifact_stage_mode"), "planning_only", "artifact_stage_mode")
    _require_equal(link.get("auto_approval"), False, "auto_approval")


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise ReviewFlowArtifactLinkError(f"{name} must be {expected!r}")
