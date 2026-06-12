import pytest

from traceleak.review_artifact_manifest import build_review_artifact_manifest
from traceleak.review_flow import build_review_flow
from traceleak.review_flow_artifact_link import (
    ReviewFlowArtifactLinkError,
    build_review_flow_artifact_link,
    validate_review_flow_artifact_link,
)
from traceleak.stage_plan import build_stage_plan


def test_build_review_flow_artifact_link_connects_p3_to_p4() -> None:
    link = build_review_flow_artifact_link(
        review_flow=build_review_flow(),
        artifact_manifest=build_review_artifact_manifest(stage_plan=build_stage_plan()),
    )

    assert link["format"] == "traceleak.review_flow_artifact_link.v1"
    assert link["mode"] == "review_only"
    assert link["flow_stage"] == "P3"
    assert link["artifact_stage"] == "P4"
    assert link["artifact_stage_mode"] == "planning_only"
    assert link["auto_approval"] is False


def test_review_flow_artifact_link_rejects_auto_approval() -> None:
    link = build_review_flow_artifact_link(
        review_flow=build_review_flow(),
        artifact_manifest=build_review_artifact_manifest(stage_plan=build_stage_plan()),
    )
    link["auto_approval"] = True

    with pytest.raises(ReviewFlowArtifactLinkError, match="auto_approval"):
        validate_review_flow_artifact_link(link)
