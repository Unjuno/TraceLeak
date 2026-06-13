"""OpenSSL materialization approval gate helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_reviewed_materialization_request import (
    validate_openssl_reviewed_materialization_request,
)

OPENSSL_MATERIALIZATION_APPROVAL_GATE_FORMAT = (
    "traceleak.openssl_materialization_approval_gate.v1"
)
OPENSSL_MATERIALIZATION_APPROVAL_RECORD_FORMAT = (
    "traceleak.openssl_materialization_approval_record.v1"
)
REQUIRED_APPROVAL_SCOPE = "reviewed_materialization_request_only"
FORBIDDEN_APPROVAL_FLAGS = [
    "source_text_embedded",
    "diff_embedded",
    "commands_embedded",
    "patch_application_allowed",
    "compile_allowed",
    "execution_allowed",
    "raw_capture_allowed",
]


class OpenSSLMaterializationApprovalGateError(ValueError):
    """Raised when an OpenSSL materialization approval gate is invalid."""


def build_openssl_materialization_approval_record(
    *,
    reviewed_request: dict[str, Any],
    reviewer: str,
    reviewed_at: str,
) -> dict[str, Any]:
    """Build a review record for a non-executable materialization request."""

    validate_openssl_reviewed_materialization_request(reviewed_request)
    record = {
        "format": OPENSSL_MATERIALIZATION_APPROVAL_RECORD_FORMAT,
        "status": "review_approved",
        "decision": "approved",
        "approval_scope": REQUIRED_APPROVAL_SCOPE,
        "request_format": reviewed_request["format"],
        "source_pin_digest": reviewed_request["source_pin_digest"],
        "trace_contract_digest": reviewed_request["trace_contract_digest"],
        "workspace_root": reviewed_request["workspace_root"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "human_review_completed": True,
        "source_text_embedded": False,
        "diff_embedded": False,
        "commands_embedded": False,
        "materialization_request_approved": True,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_materialization_approval_record(
        approval_record=record,
        reviewed_request=reviewed_request,
    )
    return record


def build_openssl_materialization_approval_gate(
    *,
    reviewed_request: dict[str, Any],
    approval_record: dict[str, Any],
) -> dict[str, Any]:
    """Build a satisfied approval gate for a reviewed materialization request."""

    validate_openssl_reviewed_materialization_request(reviewed_request)
    validate_openssl_materialization_approval_record(
        approval_record=approval_record,
        reviewed_request=reviewed_request,
    )
    gate = {
        "format": OPENSSL_MATERIALIZATION_APPROVAL_GATE_FORMAT,
        "status": "approval_gate_satisfied",
        "phase": "P9",
        "target": "openssl_materialization_approval",
        "mode": "approval_gate_only",
        "approval_scope": REQUIRED_APPROVAL_SCOPE,
        "request_format": reviewed_request["format"],
        "approval_record_format": approval_record["format"],
        "source_pin_digest": reviewed_request["source_pin_digest"],
        "trace_contract_digest": reviewed_request["trace_contract_digest"],
        "workspace_root": reviewed_request["workspace_root"],
        "approval_record_accepted": True,
        "materialization_request_approved": True,
        "materialization_allowed": True,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_materialization_approval_gate(gate)
    return gate


def validate_openssl_materialization_approval_record(
    *,
    approval_record: dict[str, Any],
    reviewed_request: dict[str, Any],
) -> None:
    """Validate a review record against the reviewed materialization request."""

    validate_openssl_reviewed_materialization_request(reviewed_request)
    _require_equal(
        approval_record.get("format"),
        OPENSSL_MATERIALIZATION_APPROVAL_RECORD_FORMAT,
        "format",
    )
    _require_equal(approval_record.get("status"), "review_approved", "status")
    _require_equal(approval_record.get("decision"), "approved", "decision")
    _require_equal(
        approval_record.get("approval_scope"),
        REQUIRED_APPROVAL_SCOPE,
        "approval_scope",
    )
    _require_equal(approval_record.get("request_format"), reviewed_request["format"], "request_format")
    _require_equal(
        approval_record.get("source_pin_digest"),
        reviewed_request["source_pin_digest"],
        "source_pin_digest",
    )
    _require_equal(
        approval_record.get("trace_contract_digest"),
        reviewed_request["trace_contract_digest"],
        "trace_contract_digest",
    )
    _require_equal(approval_record.get("workspace_root"), reviewed_request["workspace_root"], "workspace_root")
    _require_non_empty_string(approval_record.get("reviewer"), "reviewer")
    _require_non_empty_string(approval_record.get("reviewed_at"), "reviewed_at")
    _require_equal(
        approval_record.get("human_review_completed"),
        True,
        "human_review_completed",
    )
    _require_equal(
        approval_record.get("materialization_request_approved"),
        True,
        "materialization_request_approved",
    )
    for flag in FORBIDDEN_APPROVAL_FLAGS:
        _require_equal(approval_record.get(flag), False, flag)


def validate_openssl_materialization_approval_gate(gate: dict[str, Any]) -> None:
    """Validate a satisfied OpenSSL materialization approval gate."""

    _require_equal(gate.get("format"), OPENSSL_MATERIALIZATION_APPROVAL_GATE_FORMAT, "format")
    _require_equal(gate.get("status"), "approval_gate_satisfied", "status")
    _require_equal(gate.get("phase"), "P9", "phase")
    _require_equal(gate.get("target"), "openssl_materialization_approval", "target")
    _require_equal(gate.get("mode"), "approval_gate_only", "mode")
    _require_equal(gate.get("approval_scope"), REQUIRED_APPROVAL_SCOPE, "approval_scope")
    _require_equal(
        gate.get("approval_record_format"),
        OPENSSL_MATERIALIZATION_APPROVAL_RECORD_FORMAT,
        "approval_record_format",
    )
    _require_non_empty_string(gate.get("request_format"), "request_format")
    _require_non_empty_string(gate.get("source_pin_digest"), "source_pin_digest")
    _require_non_empty_string(gate.get("trace_contract_digest"), "trace_contract_digest")
    _require_non_empty_string(gate.get("workspace_root"), "workspace_root")
    _require_equal(gate.get("approval_record_accepted"), True, "approval_record_accepted")
    _require_equal(
        gate.get("materialization_request_approved"),
        True,
        "materialization_request_approved",
    )
    _require_equal(gate.get("materialization_allowed"), True, "materialization_allowed")
    _require_equal(gate.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(gate.get("compile_allowed"), False, "compile_allowed")
    _require_equal(gate.get("execution_allowed"), False, "execution_allowed")
    _require_equal(gate.get("raw_capture_allowed"), False, "raw_capture_allowed")


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLMaterializationApprovalGateError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLMaterializationApprovalGateError(f"{name} must be {expected!r}")
