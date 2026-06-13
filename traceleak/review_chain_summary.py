"""Review chain summary helpers."""

from __future__ import annotations

from typing import Any

from traceleak.review_chain_snapshot import validate_review_chain_snapshot

REVIEW_CHAIN_SUMMARY_FORMAT = "traceleak.review_chain_summary.v1"


class ReviewChainSummaryError(ValueError):
    """Raised when a review chain summary is invalid."""


def build_review_chain_summary(*, snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build a compact summary from a P3-P5 review chain snapshot."""

    validate_review_chain_snapshot(snapshot)
    summary = {
        "format": REVIEW_CHAIN_SUMMARY_FORMAT,
        "status": "ready",
        "mode": snapshot["mode"],
        "chain": snapshot["chain_contract"]["chain"],
        "review_flow_steps": list(snapshot["review_flow"]["steps"]),
        "artifact_slot_count": len(snapshot["artifact_slot_set"]["slots"]),
        "artifact_kinds": [slot["kind"] for slot in snapshot["artifact_slot_set"]["slots"]],
        "p5_requirements": list(snapshot["p5_contract"]["requirements"]),
        "activation_allowed": False,
        "auto_approval": False,
    }
    validate_review_chain_summary(summary)
    return summary


def validate_review_chain_summary(summary: dict[str, Any]) -> None:
    """Validate a compact P3-P5 review chain summary."""

    _require_equal(summary.get("format"), REVIEW_CHAIN_SUMMARY_FORMAT, "format")
    _require_equal(summary.get("status"), "ready", "status")
    _require_equal(summary.get("mode"), "review_only", "mode")
    _require_equal(summary.get("chain"), ["P3", "P4", "P5"], "chain")
    _require_positive_int(summary.get("artifact_slot_count"), "artifact_slot_count")
    _require_string_list(summary.get("review_flow_steps"), "review_flow_steps")
    _require_string_list(summary.get("artifact_kinds"), "artifact_kinds")
    _require_string_list(summary.get("p5_requirements"), "p5_requirements")
    _require_equal(summary.get("activation_allowed"), False, "activation_allowed")
    _require_equal(summary.get("auto_approval"), False, "auto_approval")


def _require_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ReviewChainSummaryError(f"{name} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise ReviewChainSummaryError(f"{name} must contain only non-empty strings")
    return value


def _require_positive_int(value: Any, name: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ReviewChainSummaryError(f"{name} must be a positive integer")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise ReviewChainSummaryError(f"{name} must be {expected!r}")
