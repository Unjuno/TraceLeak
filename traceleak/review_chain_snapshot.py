"""Review chain snapshot helpers."""

from __future__ import annotations

from typing import Any

from traceleak.p5_contract import build_p5_contract, validate_p5_contract
from traceleak.review_artifact_manifest import build_review_artifact_manifest, validate_review_artifact_manifest
from traceleak.review_artifact_slot_set import build_review_artifact_slot_set, validate_review_artifact_slot_set
from traceleak.review_chain_contract import build_review_chain_contract, validate_review_chain_contract
from traceleak.review_flow import build_review_flow, validate_review_flow
from traceleak.review_flow_artifact_link import build_review_flow_artifact_link, validate_review_flow_artifact_link
from traceleak.stage_plan import build_stage_plan, validate_stage_plan

REVIEW_CHAIN_SNAPSHOT_FORMAT = "traceleak.review_chain_snapshot.v1"


class ReviewChainSnapshotError(ValueError):
    """Raised when a review chain snapshot is invalid."""


def build_review_chain_snapshot() -> dict[str, Any]:
    """Build a complete P3-P5 review chain snapshot."""

    stage_plan = build_stage_plan()
    review_flow = build_review_flow()
    artifact_manifest = build_review_artifact_manifest(stage_plan=stage_plan)
    flow_artifact_link = build_review_flow_artifact_link(
        review_flow=review_flow,
        artifact_manifest=artifact_manifest,
    )
    artifact_slot_set = build_review_artifact_slot_set(
        artifact_manifest=artifact_manifest,
        flow_artifact_link=flow_artifact_link,
    )
    p5_contract = build_p5_contract(slot_set=artifact_slot_set)
    chain_contract = build_review_chain_contract(
        review_flow=review_flow,
        flow_artifact_link=flow_artifact_link,
        artifact_slot_set=artifact_slot_set,
        p5_contract=p5_contract,
    )
    snapshot = {
        "format": REVIEW_CHAIN_SNAPSHOT_FORMAT,
        "status": "ready",
        "mode": "review_only",
        "stage_plan": stage_plan,
        "review_flow": review_flow,
        "artifact_manifest": artifact_manifest,
        "flow_artifact_link": flow_artifact_link,
        "artifact_slot_set": artifact_slot_set,
        "p5_contract": p5_contract,
        "chain_contract": chain_contract,
        "activation_allowed": False,
        "auto_approval": False,
    }
    validate_review_chain_snapshot(snapshot)
    return snapshot


def validate_review_chain_snapshot(snapshot: dict[str, Any]) -> None:
    """Validate a complete P3-P5 review chain snapshot."""

    _require_equal(snapshot.get("format"), REVIEW_CHAIN_SNAPSHOT_FORMAT, "format")
    _require_equal(snapshot.get("status"), "ready", "status")
    _require_equal(snapshot.get("mode"), "review_only", "mode")
    _require_equal(snapshot.get("activation_allowed"), False, "activation_allowed")
    _require_equal(snapshot.get("auto_approval"), False, "auto_approval")
    validate_stage_plan(_require_dict(snapshot.get("stage_plan"), "stage_plan"))
    validate_review_flow(_require_dict(snapshot.get("review_flow"), "review_flow"))
    validate_review_artifact_manifest(_require_dict(snapshot.get("artifact_manifest"), "artifact_manifest"))
    validate_review_flow_artifact_link(_require_dict(snapshot.get("flow_artifact_link"), "flow_artifact_link"))
    validate_review_artifact_slot_set(_require_dict(snapshot.get("artifact_slot_set"), "artifact_slot_set"))
    validate_p5_contract(_require_dict(snapshot.get("p5_contract"), "p5_contract"))
    validate_review_chain_contract(_require_dict(snapshot.get("chain_contract"), "chain_contract"))


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReviewChainSnapshotError(f"{name} must be an object")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise ReviewChainSnapshotError(f"{name} must be {expected!r}")
