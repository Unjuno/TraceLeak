import json

import pytest

from traceleak.level7_review_gate import (
    LEVEL7_REVIEW_GATE_FORMAT,
    Level7ReviewGateError,
    build_level7_review_gate,
    validate_level7_review_gate,
    write_level7_review_gate,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def demo_summary():
    return build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]


def test_level7_review_gate_defaults_to_defer() -> None:
    gate = build_level7_review_gate(
        profile_demo_summary=demo_summary(),
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
    )

    assert gate["format"] == LEVEL7_REVIEW_GATE_FORMAT
    assert gate["phase"] == "P106"
    assert gate["decision"] == "defer"
    assert gate["allowances"]["planning_only"] is False
    assert gate["allowances"]["direct_action_enabled"] is False
    assert gate["allowances"]["source_change_enabled"] is False
    assert gate["allowances"]["payload_collection_enabled"] is False
    assert gate["allowances"]["claim_enabled"] is False
    validate_level7_review_gate(gate)


def test_level7_review_gate_can_approve_planning_only() -> None:
    gate = build_level7_review_gate(
        profile_demo_summary=demo_summary(),
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
        decision="approve_planning_only",
    )

    assert gate["allowances"]["planning_only"] is True
    assert gate["allowances"]["direct_action_enabled"] is False


def test_level7_review_gate_writes_json(tmp_path) -> None:
    gate = build_level7_review_gate(
        profile_demo_summary=demo_summary(),
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
    )
    path = tmp_path / "level7-review-gate.json"

    write_level7_review_gate(path, gate)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL7_REVIEW_GATE_FORMAT


def test_level7_review_gate_rejects_bad_decision() -> None:
    with pytest.raises(Level7ReviewGateError, match="decision"):
        build_level7_review_gate(
            profile_demo_summary=demo_summary(),
            reviewer="reviewer",
            reviewed_at="2026-06-15T00:00:00Z",
            decision="approve_direct_action",
        )


def test_level7_review_gate_rejects_claim_enabled() -> None:
    gate = build_level7_review_gate(
        profile_demo_summary=demo_summary(),
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
    )
    gate["allowances"]["claim_enabled"] = True

    with pytest.raises(Level7ReviewGateError, match="claim_enabled"):
        validate_level7_review_gate(gate)
