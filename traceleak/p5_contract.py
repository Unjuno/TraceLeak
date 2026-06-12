"""P5 design-only contract helpers."""

from __future__ import annotations

from typing import Any

from traceleak.review_artifact_slot_set import validate_review_artifact_slot_set

P5_CONTRACT_FORMAT = "traceleak.p5_contract.v1"
P5_REQUIREMENTS = [
    "manual_review",
    "separate_workspace",
    "fixed_revision",
    "redacted_schema",
    "post_check",
    "control_case",
    "cleanup_note",
]


class P5ContractError(ValueError):
    """Raised when a P5 contract is invalid."""


def build_p5_contract(*, slot_set: dict[str, Any]) -> dict[str, Any]:
    """Build a P5 design-only contract from a P4 slot set."""

    validate_review_artifact_slot_set(slot_set)
    contract = {
        "format": P5_CONTRACT_FORMAT,
        "status": "ready",
        "mode": "design_only",
        "stage": "P5",
        "source_stage": slot_set["stage"],
        "source_stage_mode": slot_set["stage_mode"],
        "requirements": list(P5_REQUIREMENTS),
        "activation_allowed": False,
        "auto_approval": False,
    }
    validate_p5_contract(contract)
    return contract


def validate_p5_contract(contract: dict[str, Any]) -> None:
    """Validate a P5 design-only contract."""

    _require_equal(contract.get("format"), P5_CONTRACT_FORMAT, "format")
    _require_equal(contract.get("status"), "ready", "status")
    _require_equal(contract.get("mode"), "design_only", "mode")
    _require_equal(contract.get("stage"), "P5", "stage")
    _require_equal(contract.get("source_stage"), "P4", "source_stage")
    _require_equal(contract.get("source_stage_mode"), "planning_only", "source_stage_mode")
    _require_equal(contract.get("activation_allowed"), False, "activation_allowed")
    _require_equal(contract.get("auto_approval"), False, "auto_approval")
    requirements = _require_string_list(contract.get("requirements"), "requirements")
    missing = sorted(set(P5_REQUIREMENTS) - set(requirements))
    if missing:
        raise P5ContractError(f"requirements missing: {', '.join(missing)}")


def _require_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise P5ContractError(f"{name} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise P5ContractError(f"{name} must contain only non-empty strings")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise P5ContractError(f"{name} must be {expected!r}")
