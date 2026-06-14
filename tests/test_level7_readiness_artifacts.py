import json

import pytest

from traceleak.level7_review_gate import (
    LEVEL7_REVIEW_CHECKLIST_FORMAT,
    Level7ReviewGateError,
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_checklist,
    build_level7_review_gate,
    render_level7_readiness_report,
    validate_level7_readiness_report,
    validate_level7_review_checklist,
    write_level7_readiness_report,
    write_level7_review_checklist,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def artifacts():
    summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]
    gate = build_level7_review_gate(
        profile_demo_summary=summary,
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
        decision="approve_planning_only",
    )
    contract = build_level7_planning_contract(review_gate=gate)
    boundary = build_level7_artifact_boundary_plan(planning_contract=contract)
    checklist = build_level7_review_checklist(artifact_boundary_plan=boundary)
    return gate, contract, boundary, checklist


def test_level7_review_checklist_builds_all_required_items() -> None:
    _, _, _, checklist = artifacts()

    assert checklist["format"] == LEVEL7_REVIEW_CHECKLIST_FORMAT
    assert checklist["phase"] == "P109"
    assert all(checklist["items"].values())
    assert checklist["items"]["direct_action_disabled"] is True
    assert checklist["items"]["payload_collection_disabled"] is True
    assert checklist["items"]["claim_disabled"] is True
    validate_level7_review_checklist(checklist)


def test_level7_review_checklist_rejects_false_item() -> None:
    _, _, _, checklist = artifacts()
    checklist["items"]["claim_disabled"] = False

    with pytest.raises(Level7ReviewGateError, match="claim_disabled"):
        validate_level7_review_checklist(checklist)


def test_level7_review_checklist_writer(tmp_path) -> None:
    _, _, _, checklist = artifacts()
    path = tmp_path / "level7-review-checklist.json"

    write_level7_review_checklist(path, checklist)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["format"] == LEVEL7_REVIEW_CHECKLIST_FORMAT


def test_level7_readiness_report_renders_required_sections() -> None:
    gate, contract, boundary, checklist = artifacts()

    markdown = render_level7_readiness_report(
        review_gate=gate,
        planning_contract=contract,
        artifact_boundary_plan=boundary,
        checklist=checklist,
    )

    assert "# Level 7 Readiness Report" in markdown
    assert "## Level 6 baseline status" in markdown
    assert "## Review gate status" in markdown
    assert "## Artifact boundary" in markdown
    assert "No external execution is authorized." in markdown
    assert "No source mutation is authorized." in markdown
    assert "No payload collection is authorized." in markdown
    assert "No claim is authorized." in markdown
    validate_level7_readiness_report(markdown)


def test_level7_readiness_report_writer(tmp_path) -> None:
    gate, contract, boundary, checklist = artifacts()
    markdown = render_level7_readiness_report(
        review_gate=gate,
        planning_contract=contract,
        artifact_boundary_plan=boundary,
        checklist=checklist,
    )
    path = tmp_path / "level7-readiness.md"

    write_level7_readiness_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 7 Readiness Report")
