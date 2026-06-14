import json

import pytest

from traceleak.level7_review_gate import (
    LEVEL7_PLANNING_CONTRACT_FORMAT,
    Level7ReviewGateError,
    build_level7_planning_contract,
    build_level7_review_gate,
    validate_level7_planning_contract,
    write_level7_planning_contract,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def summary():
    return build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]


def planning_gate():
    return build_level7_review_gate(
        profile_demo_summary=summary(),
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
        decision="approve_planning_only",
    )


def test_planning_contract_requires_planning_approval() -> None:
    gate = build_level7_review_gate(
        profile_demo_summary=summary(),
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
    )

    with pytest.raises(Level7ReviewGateError, match="approve planning only"):
        build_level7_planning_contract(review_gate=gate)


def test_planning_contract_builds_from_approved_gate() -> None:
    contract = build_level7_planning_contract(review_gate=planning_gate())

    assert contract["format"] == LEVEL7_PLANNING_CONTRACT_FORMAT
    assert contract["phase"] == "P107"
    assert contract["review_decision"] == "approve_planning_only"
    assert contract["allowances"]["planning_only"] is True
    assert contract["allowances"]["direct_action_enabled"] is False
    assert contract["allowances"]["source_change_enabled"] is False
    assert contract["allowances"]["payload_collection_enabled"] is False
    assert contract["allowances"]["claim_enabled"] is False
    validate_level7_planning_contract(contract)


def test_planning_contract_accepts_subset_of_allowed_tasks() -> None:
    contract = build_level7_planning_contract(
        review_gate=planning_gate(),
        tasks=["metadata_ingress_review", "report_surface_review"],
    )

    assert contract["tasks"] == ["metadata_ingress_review", "report_surface_review"]


def test_planning_contract_rejects_unknown_task() -> None:
    with pytest.raises(Level7ReviewGateError, match="not allowed"):
        build_level7_planning_contract(
            review_gate=planning_gate(),
            tasks=["unknown_task"],
        )


def test_planning_contract_rejects_forbidden_task() -> None:
    with pytest.raises(Level7ReviewGateError, match="forbidden"):
        build_level7_planning_contract(
            review_gate=planning_gate(),
            tasks=["external_run"],
        )


def test_planning_contract_writer(tmp_path) -> None:
    contract = build_level7_planning_contract(review_gate=planning_gate())
    path = tmp_path / "level7-planning-contract.json"

    write_level7_planning_contract(path, contract)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["format"] == LEVEL7_PLANNING_CONTRACT_FORMAT
    assert loaded["allowances"]["claim_enabled"] is False
