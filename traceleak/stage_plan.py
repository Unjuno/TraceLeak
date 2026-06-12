"""Static P0-P5 stage plan helpers."""

from __future__ import annotations

from typing import Any

STAGE_PLAN_FORMAT = "traceleak.stage_plan.v1"
STAGES = ["P0", "P1", "P2", "P3", "P4", "P5"]


class StagePlanError(ValueError):
    """Raised when a stage plan is invalid."""


def build_stage_plan() -> dict[str, Any]:
    """Return the current P0-P5 stage plan."""

    plan = {
        "format": STAGE_PLAN_FORMAT,
        "status": "ready",
        "mode": "review_only",
        "stages": list(STAGES),
        "completed": ["P0", "P2"],
        "active": ["P1", "P3", "P4", "P5"],
        "activation": {
            "P3": "notes_only",
            "P4": "planning_only",
            "P5": "design_only",
        },
    }
    validate_stage_plan(plan)
    return plan


def validate_stage_plan(plan: dict[str, Any]) -> None:
    """Validate a P0-P5 stage plan."""

    _require_equal(plan.get("format"), STAGE_PLAN_FORMAT, "format")
    _require_equal(plan.get("status"), "ready", "status")
    _require_equal(plan.get("mode"), "review_only", "mode")
    stages = _require_string_list(plan.get("stages"), "stages")
    missing = sorted(set(STAGES) - set(stages))
    if missing:
        raise StagePlanError(f"stages missing: {', '.join(missing)}")
    _require_string_list(plan.get("completed"), "completed")
    _require_string_list(plan.get("active"), "active")
    activation = plan.get("activation")
    if not isinstance(activation, dict):
        raise StagePlanError("activation must be an object")
    _require_equal(activation.get("P3"), "notes_only", "activation.P3")
    _require_equal(activation.get("P4"), "planning_only", "activation.P4")
    _require_equal(activation.get("P5"), "design_only", "activation.P5")


def _require_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise StagePlanError(f"{name} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise StagePlanError(f"{name} must contain only non-empty strings")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise StagePlanError(f"{name} must be {expected!r}")
