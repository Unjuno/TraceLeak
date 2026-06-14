import json

import pytest

from traceleak.level7_review_gate import (
    LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT,
    Level7ReviewGateError,
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_gate,
    validate_level7_artifact_boundary_plan,
    write_level7_artifact_boundary_plan,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def planning_contract():
    summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]
    gate = build_level7_review_gate(
        profile_demo_summary=summary,
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
        decision="approve_planning_only",
    )
    return build_level7_planning_contract(review_gate=gate)


def test_artifact_boundary_plan_builds_from_planning_contract() -> None:
    plan = build_level7_artifact_boundary_plan(planning_contract=planning_contract())

    assert plan["format"] == LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT
    assert plan["phase"] == "P108"
    assert plan["output_root"] == "reports/local"
    assert "profile_json" in plan["accepted_artifact_classes"]
    assert "private_material" in plan["rejected_artifact_classes"]
    assert plan["path_constraints"]["absolute_paths_allowed"] is False
    assert plan["path_constraints"]["parent_traversal_allowed"] is False
    assert plan["content_rules"]["path_only_indexing_allowed"] is True
    assert plan["content_rules"]["payload_reading_allowed"] is False
    assert plan["content_rules"]["claim_generation_allowed"] is False
    validate_level7_artifact_boundary_plan(plan)


def test_artifact_boundary_plan_rejects_bad_root() -> None:
    with pytest.raises(Level7ReviewGateError, match="reports/local"):
        build_level7_artifact_boundary_plan(
            planning_contract=planning_contract(),
            output_root="artifacts/local",
        )


def test_artifact_boundary_plan_rejects_parent_traversal() -> None:
    with pytest.raises(Level7ReviewGateError, match="relative"):
        build_level7_artifact_boundary_plan(
            planning_contract=planning_contract(),
            output_root="../reports/local",
        )


def test_artifact_boundary_plan_rejects_payload_reading() -> None:
    plan = build_level7_artifact_boundary_plan(planning_contract=planning_contract())
    plan["content_rules"]["payload_reading_allowed"] = True

    with pytest.raises(Level7ReviewGateError, match="payload_reading_allowed"):
        validate_level7_artifact_boundary_plan(plan)


def test_artifact_boundary_plan_writer(tmp_path) -> None:
    plan = build_level7_artifact_boundary_plan(planning_contract=planning_contract())
    path = tmp_path / "level7-artifact-boundary-plan.json"

    write_level7_artifact_boundary_plan(path, plan)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["format"] == LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT
    assert loaded["content_rules"]["claim_generation_allowed"] is False
