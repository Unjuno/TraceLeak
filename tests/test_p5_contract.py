import pytest

from traceleak.p5_contract import P5ContractError, build_p5_contract, validate_p5_contract
from traceleak.review_artifact_manifest import build_review_artifact_manifest
from traceleak.review_artifact_slot_set import build_review_artifact_slot_set
from traceleak.review_flow import build_review_flow
from traceleak.review_flow_artifact_link import build_review_flow_artifact_link
from traceleak.stage_plan import build_stage_plan


def make_p5_contract() -> dict:
    manifest = build_review_artifact_manifest(stage_plan=build_stage_plan())
    link = build_review_flow_artifact_link(
        review_flow=build_review_flow(),
        artifact_manifest=manifest,
    )
    slot_set = build_review_artifact_slot_set(
        artifact_manifest=manifest,
        flow_artifact_link=link,
    )
    return build_p5_contract(slot_set=slot_set)


def test_build_p5_contract_is_design_only_from_p4_slot_set() -> None:
    contract = make_p5_contract()

    assert contract["format"] == "traceleak.p5_contract.v1"
    assert contract["mode"] == "design_only"
    assert contract["stage"] == "P5"
    assert contract["source_stage"] == "P4"
    assert contract["source_stage_mode"] == "planning_only"
    assert contract["activation_allowed"] is False
    assert contract["auto_approval"] is False


def test_p5_contract_rejects_activation_allowed() -> None:
    contract = make_p5_contract()
    contract["activation_allowed"] = True

    with pytest.raises(P5ContractError, match="activation_allowed"):
        validate_p5_contract(contract)


def test_p5_contract_rejects_auto_approval() -> None:
    contract = make_p5_contract()
    contract["auto_approval"] = True

    with pytest.raises(P5ContractError, match="auto_approval"):
        validate_p5_contract(contract)


def test_p5_contract_rejects_missing_requirement() -> None:
    contract = make_p5_contract()
    contract["requirements"] = ["manual_review"]

    with pytest.raises(P5ContractError, match="requirements missing"):
        validate_p5_contract(contract)
