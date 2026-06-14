import json

import pytest

from traceleak.level7_review_gate import (
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_gate,
)
from traceleak.level8_artifact_intake import (
    LEVEL8_ARTIFACT_INTAKE_MANIFEST_FORMAT,
    Level8ArtifactIntakeError,
    build_level8_artifact_intake_manifest,
    validate_level8_artifact_intake_manifest,
    write_level8_artifact_intake_manifest,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def boundary_plan():
    summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]
    gate = build_level7_review_gate(
        profile_demo_summary=summary,
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
        decision="approve_planning_only",
    )
    contract = build_level7_planning_contract(review_gate=gate)
    return build_level7_artifact_boundary_plan(planning_contract=contract)


def test_manifest_builds_default_entries() -> None:
    manifest = build_level8_artifact_intake_manifest(artifact_boundary_plan=boundary_plan())

    assert manifest["format"] == LEVEL8_ARTIFACT_INTAKE_MANIFEST_FORMAT
    assert manifest["phase"] == "P114"
    assert manifest["payload_reading_allowed"] is False
    assert manifest["claim_generation_allowed"] is False
    assert len(manifest["entries"]) >= 1
    assert {item["artifact_class"] for item in manifest["entries"]} <= set(
        manifest["accepted_artifact_classes"]
    )
    validate_level8_artifact_intake_manifest(manifest)


def test_manifest_rejects_rejected_artifact_class() -> None:
    entries = [
        {
            "key": "raw",
            "artifact_class": "payload_dump",
            "relative_path": "reports/local/raw.txt",
            "role": "raw artifact",
        }
    ]

    with pytest.raises(Level8ArtifactIntakeError, match="rejected"):
        build_level8_artifact_intake_manifest(artifact_boundary_plan=boundary_plan(), entries=entries)


def test_manifest_rejects_unknown_artifact_class() -> None:
    entries = [
        {
            "key": "unknown",
            "artifact_class": "unknown_json",
            "relative_path": "reports/local/unknown.json",
            "role": "unknown artifact",
        }
    ]

    with pytest.raises(Level8ArtifactIntakeError, match="not accepted"):
        build_level8_artifact_intake_manifest(artifact_boundary_plan=boundary_plan(), entries=entries)


def test_manifest_rejects_duplicate_keys() -> None:
    entries = [
        {
            "key": "dup",
            "artifact_class": "summary_json",
            "relative_path": "reports/local/a.json",
            "role": "summary a",
        },
        {
            "key": "dup",
            "artifact_class": "summary_json",
            "relative_path": "reports/local/b.json",
            "role": "summary b",
        },
    ]

    with pytest.raises(Level8ArtifactIntakeError, match="unique"):
        build_level8_artifact_intake_manifest(artifact_boundary_plan=boundary_plan(), entries=entries)


def test_manifest_rejects_unsafe_path() -> None:
    entries = [
        {
            "key": "bad_path",
            "artifact_class": "summary_json",
            "relative_path": "../reports/local/a.json",
            "role": "summary",
        }
    ]

    with pytest.raises(Level8ArtifactIntakeError, match="relative"):
        build_level8_artifact_intake_manifest(artifact_boundary_plan=boundary_plan(), entries=entries)


def test_manifest_rejects_payload_reading_enabled() -> None:
    manifest = build_level8_artifact_intake_manifest(artifact_boundary_plan=boundary_plan())
    manifest["payload_reading_allowed"] = True

    with pytest.raises(Level8ArtifactIntakeError, match="payload_reading_allowed"):
        validate_level8_artifact_intake_manifest(manifest)


def test_manifest_writer(tmp_path) -> None:
    manifest = build_level8_artifact_intake_manifest(artifact_boundary_plan=boundary_plan())
    path = tmp_path / "level8-artifact-intake-manifest.json"

    write_level8_artifact_intake_manifest(path, manifest)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["format"] == LEVEL8_ARTIFACT_INTAKE_MANIFEST_FORMAT
