"""Review chain contract helpers."""

from __future__ import annotations

from typing import Any

from traceleak.p5_contract import validate_p5_contract
from traceleak.review_artifact_slot_set import validate_review_artifact_slot_set
from traceleak.review_flow import validate_review_flow
from traceleak.review_flow_artifact_link import validate_review_flow_artifact_link

REVIEW_CHAIN_CONTRACT_FORMAT = "traceleak.review_chain_contract.v1"


class ReviewChainContractError(ValueError):
    """Raised when a review chain contract is invalid."""


def build_review_chain_contract(
    *,
    review_flow: dict[str, Any],
    flow_artifact_link: dict[str, Any],
    artifact_slot_set: dict[str, Any],
    p5_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build a P3-P5 review chain contract."""

    validate_review_flow(review_flow)
    validate_review_flow_artifact_link(flow_artifact_link)
    validate_review_artifact_slot_set(artifact_slot_set)
    validate_p5_contract(p5_contract)
    contract = {
        "format": REVIEW_CHAIN_CONTRACT_FORMAT,
        "status": "ready",
        "mode": "review_only",
        "chain": [
            review_flow["stage"],
            flow_artifact_link["artifact_stage"],
            p5_contract["stage"],
        ],
        "p4_stage_mode": artifact_slot_set["stage_mode"],
        "p5_mode": p5_contract["mode"],
        "activation_allowed": False,
        "auto_approval": False,
    }
    validate_review_chain_contract(contract)
    return contract


def validate_review_chain_contract(contract: dict[str, Any]) -> None:
    """Validate a P3-P5 review chain contract."""

    _require_equal(contract.get("format"), REVIEW_CHAIN_CONTRACT_FORMAT, "format")
    _require_equal(contract.get("status"), "ready", "status")
    _require_equal(contract.get("mode"), "review_only", "mode")
    _require_equal(contract.get("chain"), ["P3", "P4", "P5"], "chain")
    _require_equal(contract.get("p4_stage_mode"), "planning_only", "p4_stage_mode")
    _require_equal(contract.get("p5_mode"), "design_only", "p5_mode")
    _require_equal(contract.get("activation_allowed"), False, "activation_allowed")
    _require_equal(contract.get("auto_approval"), False, "auto_approval")


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise ReviewChainContractError(f"{name} must be {expected!r}")
