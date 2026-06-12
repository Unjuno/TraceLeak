"""Review flow contract helpers."""

from __future__ import annotations

from typing import Any

REVIEW_FLOW_FORMAT = "traceleak.review_flow.v1"
REVIEW_FLOW_STEPS = [
    "verify_local",
    "check_template",
    "extract_skeleton",
    "review_record",
    "check_record",
]


class ReviewFlowError(ValueError):
    """Raised when a review flow contract is invalid."""


def build_review_flow() -> dict[str, Any]:
    """Build the P3 review flow contract."""

    flow = {
        "format": REVIEW_FLOW_FORMAT,
        "status": "ready",
        "mode": "review_only",
        "stage": "P3",
        "steps": list(REVIEW_FLOW_STEPS),
        "template_state": "pending",
        "record_state": "human_edited",
        "auto_approval": False,
    }
    validate_review_flow(flow)
    return flow


def validate_review_flow(flow: dict[str, Any]) -> None:
    """Validate the P3 review flow contract."""

    _require_equal(flow.get("format"), REVIEW_FLOW_FORMAT, "format")
    _require_equal(flow.get("status"), "ready", "status")
    _require_equal(flow.get("mode"), "review_only", "mode")
    _require_equal(flow.get("stage"), "P3", "stage")
    steps = _require_string_list(flow.get("steps"), "steps")
    missing = sorted(set(REVIEW_FLOW_STEPS) - set(steps))
    if missing:
        raise ReviewFlowError(f"steps missing: {', '.join(missing)}")
    _require_equal(flow.get("template_state"), "pending", "template_state")
    _require_equal(flow.get("record_state"), "human_edited", "record_state")
    _require_equal(flow.get("auto_approval"), False, "auto_approval")


def _require_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ReviewFlowError(f"{name} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise ReviewFlowError(f"{name} must contain only non-empty strings")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise ReviewFlowError(f"{name} must be {expected!r}")
