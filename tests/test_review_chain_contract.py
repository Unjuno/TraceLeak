import pytest

from traceleak.p5_contract import build_p5_contract
from traceleak.review_artifact_manifest import build_review_artifact_manifest
from traceleak.review_artifact_slot_set import build_review_artifact_slot_set
from traceleak.review_chain_contract import (
    ReviewChainContractError,
    build_review_chain_contract,
    validate_review_chain_contract,
)
from traceleak.review_flow import build_review_flow
from traceleak.review_flow_artifact_link import build_review_flow_artifact_link
from traceleak.stage_plan import build_stage_plan


def make_review_chain_contract() -> dict:
    flow = build_review_flow()
    manifest = build_review_artifact_manifest(stage_plan=build_stage_plan())
    link = build_review_flow_artifact_link(
        review_flow=flow,
        artifact_manifest=manifest,
    )
    slot_set = build_review_artifact_slot_set(
        artifact_manifest=manifest,
        flow_artifact_link=link,
    )
    p5_contract = build_p5_contract(slot_set=slot_set)
    return build_review_chain_contract(
        review_flow=flow,
        flow_artifact_link=link,
        artifact_slot_set=slot_set,
        p5_contract=p5_contract,
    )


def test_build_review_chain_contract_links_p3_p4_p5() -> None:
    contract = make_review_chain_contract()

    assert contract["format"] == "traceleak.review_chain_contract.v1"
    assert contract["mode"] == "review_only"
    assert contract["chain"] == ["P3", "P4", "P5"]
    assert contract["p4_stage_mode"] == "planning_only"
    assert contract["p5_mode"] == "design_only"
    assert contract["activation_allowed"] is False
    assert contract["auto_approval"] is False


def test_review_chain_contract_rejects_activation_allowed() -> None:
    contract = make_review_chain_contract()
    contract["activation_allowed"] = True

    with pytest.raises(ReviewChainContractError, match="activation_allowed"):
        validate_review_chain_contract(contract)


def test_review_chain_contract_rejects_wrong_chain_order() -> None:
    contract = make_review_chain_contract()
    contract["chain"] = ["P4", "P3", "P5"]

    with pytest.raises(ReviewChainContractError, match="chain"):
        validate_review_chain_contract(contract)
