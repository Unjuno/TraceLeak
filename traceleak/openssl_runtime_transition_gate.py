"""OpenSSL runtime transition gate helpers.

This gate records the reviewed conditions required before any later local-only
OpenSSL runtime work. It does not itself enable runtime actions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OPENSSL_RUNTIME_TRANSITION_GATE_FORMAT = "traceleak.openssl_runtime_transition_gate.v1"
REQUIRED_TARGET_DECISION = "constant_time_helper_misuse_path"


class OpenSSLRuntimeTransitionGateError(ValueError):
    """Raised when an OpenSSL runtime transition gate is invalid."""


def build_openssl_runtime_transition_gate(
    *,
    reviewer: str,
    reviewed_at: str,
    target_decision: str = REQUIRED_TARGET_DECISION,
    redaction_policy: str = "metadata_only_symbolic_tokens",
) -> dict[str, Any]:
    """Build a conservative P28 runtime transition gate."""

    gate = {
        "format": OPENSSL_RUNTIME_TRANSITION_GATE_FORMAT,
        "status": "runtime_transition_gate_ready",
        "phase": "P28",
        "target": "openssl_runtime_transition_gate",
        "mode": "review_gate_only",
        "target_decision": target_decision,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "redaction_policy": redaction_policy,
        "conditions": {
            "target_selection_reviewed": True,
            "local_workspace_required": True,
            "redaction_policy_required": True,
            "reproducibility_metadata_required": True,
            "source_patch_separate_approval_required": True,
            "runtime_action_enabled": False,
            "payload_access_enabled": False,
        },
        "notes": [
            "P28 records conditions for a future local-only OpenSSL transition.",
            "This gate does not enable OpenSSL runtime actions or payload access.",
        ],
    }
    validate_openssl_runtime_transition_gate(gate)
    return gate


def validate_openssl_runtime_transition_gate(gate: dict[str, Any]) -> None:
    """Validate a conservative P28 runtime transition gate."""

    _eq(gate.get("format"), OPENSSL_RUNTIME_TRANSITION_GATE_FORMAT, "format")
    _eq(gate.get("status"), "runtime_transition_gate_ready", "status")
    _eq(gate.get("phase"), "P28", "phase")
    _eq(gate.get("target"), "openssl_runtime_transition_gate", "target")
    _eq(gate.get("mode"), "review_gate_only", "mode")
    _eq(gate.get("target_decision"), REQUIRED_TARGET_DECISION, "target_decision")
    _non_empty(gate.get("reviewer"), "reviewer")
    _non_empty(gate.get("reviewed_at"), "reviewed_at")
    _eq(gate.get("redaction_policy"), "metadata_only_symbolic_tokens", "redaction_policy")
    conditions = _dict(gate.get("conditions"), "conditions")
    for flag in [
        "target_selection_reviewed",
        "local_workspace_required",
        "redaction_policy_required",
        "reproducibility_metadata_required",
        "source_patch_separate_approval_required",
    ]:
        _eq(conditions.get(flag), True, f"conditions.{flag}")
    for flag in ["runtime_action_enabled", "payload_access_enabled"]:
        _eq(conditions.get(flag), False, f"conditions.{flag}")


def write_openssl_runtime_transition_gate(path: Path, gate: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLRuntimeTransitionGateError(f"{name} must be an object")
    return value


def _non_empty(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise OpenSSLRuntimeTransitionGateError(f"{name} must be a non-empty string")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLRuntimeTransitionGateError(f"{name} must be {expected!r}")
