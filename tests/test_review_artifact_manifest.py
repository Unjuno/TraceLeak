import pytest

from traceleak.review_artifact_manifest import (
    REVIEW_ARTIFACT_KINDS,
    ReviewArtifactManifestError,
    build_review_artifact_manifest,
    validate_review_artifact_manifest,
)
from traceleak.stage_plan import build_stage_plan


def test_build_review_artifact_manifest_from_stage_plan() -> None:
    manifest = build_review_artifact_manifest(stage_plan=build_stage_plan())

    assert manifest["format"] == "traceleak.review_artifact_manifest.v1"
    assert manifest["mode"] == "review_only"
    assert manifest["stage"] == "P4"
    assert manifest["stage_mode"] == "planning_only"
    assert manifest["artifact_kinds"] == REVIEW_ARTIFACT_KINDS


def test_review_artifact_manifest_rejects_missing_kind() -> None:
    manifest = build_review_artifact_manifest(stage_plan=build_stage_plan())
    manifest["artifact_kinds"] = ["summary_file"]

    with pytest.raises(ReviewArtifactManifestError, match="artifact_kinds missing"):
        validate_review_artifact_manifest(manifest)
