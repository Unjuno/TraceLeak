"""Review gate before moving beyond Level 6 metadata-profile work."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_derived_metadata_profile_demo_chain import (
    OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT,
    validate_openssl_derived_metadata_profile_demo_summary,
)

LEVEL7_REVIEW_GATE_FORMAT = "traceleak.level7_review_gate.v1"
LEVEL7_REVIEW_GATE_PHASE = "P106"
ALLOWED_LEVEL7_REVIEW_DECISIONS = {
    "defer",
    "approve_planning_only",
}


class Level7ReviewGateError(ValueError):
    """Raised when a Level 7 review gate is invalid."""


def build_level7_review_gate(
    *,
    profile_demo_summary: dict[str, Any],
    reviewer: str,
    reviewed_at: str,
    decision: str = "defer",
    rationale: str = "Level 7 requires explicit review before any broader proximity work.",
) -> dict[str, Any]:
    """Build a conservative review gate from a validated Level 6 summary."""

    validate_openssl_derived_metadata_profile_demo_summary(profile_demo_summary)
    _non_empty(reviewer, "reviewer")
    _non_empty(reviewed_at, "reviewed_at")
    _non_empty(rationale, "rationale")
    if decision not in ALLOWED_LEVEL7_REVIEW_DECISIONS:
        raise Level7ReviewGateError("decision is not allowed")
    flags = profile_demo_summary["flags"]
    gate = {
        "format": LEVEL7_REVIEW_GATE_FORMAT,
        "phase": LEVEL7_REVIEW_GATE_PHASE,
        "source_summary_format": profile_demo_summary["format"],
        "source_summary_phase": profile_demo_summary["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "decision": decision,
        "rationale": rationale,
        "level6_status": {
            "profile_to_adapter": profile_demo_summary["bridge_summary"]["profile_to_adapter"],
            "adapter_to_model_sequence": profile_demo_summary["bridge_summary"]["adapter_to_model_sequence"],
            "baseline_generated": profile_demo_summary["bridge_summary"]["baseline_generated"],
            "nn_generated": profile_demo_summary["bridge_summary"]["nn_generated"],
        },
        "safety_flags": {
            "metadata_only": flags["metadata_only"],
            "payload_free": flags["payload_free"],
            "public_safe": flags["public_safe"],
            "payload_inspected": flags["payload_inspected"],
            "openssl_leakage_claim": flags["openssl_leakage_claim"],
        },
        "allowances": {
            "planning_only": decision == "approve_planning_only",
            "direct_action_enabled": False,
            "source_change_enabled": False,
            "payload_collection_enabled": False,
            "claim_enabled": False,
        },
        "requirements_before_next_step": [
            "Preserve metadata-only ingress.",
            "Keep payload collection disabled.",
            "Keep source-change actions disabled.",
            "Keep claims disabled until independently reviewed evidence exists.",
        ],
    }
    validate_level7_review_gate(gate)
    return gate


def validate_level7_review_gate(gate: dict[str, Any]) -> None:
    """Validate Level 7 review gate shape."""

    if not isinstance(gate, dict):
        raise Level7ReviewGateError("gate must be an object")
    _eq(gate.get("format"), LEVEL7_REVIEW_GATE_FORMAT, "gate.format")
    _eq(gate.get("phase"), LEVEL7_REVIEW_GATE_PHASE, "gate.phase")
    _eq(
        gate.get("source_summary_format"),
        OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT,
        "gate.source_summary_format",
    )
    _eq(gate.get("source_summary_phase"), "P99", "gate.source_summary_phase")
    _non_empty(gate.get("reviewer"), "gate.reviewer")
    _non_empty(gate.get("reviewed_at"), "gate.reviewed_at")
    if gate.get("decision") not in ALLOWED_LEVEL7_REVIEW_DECISIONS:
        raise Level7ReviewGateError("gate.decision is not allowed")
    _non_empty(gate.get("rationale"), "gate.rationale")
    level6_status = gate.get("level6_status")
    if not isinstance(level6_status, dict):
        raise Level7ReviewGateError("gate.level6_status must be an object")
    for key in ["profile_to_adapter", "adapter_to_model_sequence", "baseline_generated", "nn_generated"]:
        _eq(level6_status.get(key), True, f"gate.level6_status.{key}")
    safety_flags = gate.get("safety_flags")
    if not isinstance(safety_flags, dict):
        raise Level7ReviewGateError("gate.safety_flags must be an object")
    for key in ["metadata_only", "payload_free", "public_safe"]:
        _eq(safety_flags.get(key), True, f"gate.safety_flags.{key}")
    _eq(safety_flags.get("payload_inspected"), False, "gate.safety_flags.payload_inspected")
    _eq(safety_flags.get("openssl_leakage_claim"), False, "gate.safety_flags.openssl_leakage_claim")
    allowances = gate.get("allowances")
    if not isinstance(allowances, dict):
        raise Level7ReviewGateError("gate.allowances must be an object")
    if allowances.get("planning_only") not in {True, False}:
        raise Level7ReviewGateError("gate.allowances.planning_only must be boolean")
    for key in [
        "direct_action_enabled",
        "source_change_enabled",
        "payload_collection_enabled",
        "claim_enabled",
    ]:
        _eq(allowances.get(key), False, f"gate.allowances.{key}")
    requirements = gate.get("requirements_before_next_step")
    if not isinstance(requirements, list) or len(requirements) < 4:
        raise Level7ReviewGateError("gate.requirements_before_next_step must list requirements")
    for index, item in enumerate(requirements):
        _non_empty(item, f"gate.requirements_before_next_step[{index}]")


def write_level7_review_gate(path: Path, gate: dict[str, Any]) -> None:
    """Write Level 7 review gate JSON."""

    validate_level7_review_gate(gate)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _non_empty(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise Level7ReviewGateError(f"{name} must be a non-empty string")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level7ReviewGateError(f"{name} must be {expected!r}")
