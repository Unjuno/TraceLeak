"""OpenSSL reviewed materialization request helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_isolated_execution_plan import validate_openssl_isolated_execution_plan

OPENSSL_REVIEWED_MATERIALIZATION_REQUEST_FORMAT = (
    "traceleak.openssl_reviewed_materialization_request.v1"
)
REQUEST_CHECKS = [
    "human_review_required",
    "approval_record_required",
    "scope_bound_to_isolated_workspace",
    "source_pin_digest_bound",
    "trace_contract_digest_bound",
    "no_source_text_embedded",
    "no_diff_embedded",
    "no_commands_embedded",
]


class OpenSSLReviewedMaterializationRequestError(ValueError):
    """Raised when an OpenSSL reviewed materialization request is invalid."""


def build_openssl_reviewed_materialization_request(
    *,
    execution_plan: dict[str, Any],
) -> dict[str, Any]:
    """Build a non-materialized request for future reviewed OpenSSL materialization."""

    validate_openssl_isolated_execution_plan(execution_plan)
    request = {
        "format": OPENSSL_REVIEWED_MATERIALIZATION_REQUEST_FORMAT,
        "status": "request_draft",
        "phase": "P8",
        "target": "openssl_reviewed_materialization",
        "mode": "request_only",
        "source_pin_digest": execution_plan["source_pin_digest"],
        "trace_contract_digest": execution_plan["trace_contract_digest"],
        "workspace_root": execution_plan["workspace_root"],
        "checks": {check: True for check in REQUEST_CHECKS},
        "approval_required": True,
        "human_review_required": True,
        "source_text_embedded": False,
        "diff_embedded": False,
        "commands_embedded": False,
        "materialization_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_reviewed_materialization_request(request)
    return request


def validate_openssl_reviewed_materialization_request(request: dict[str, Any]) -> None:
    """Validate a non-materialized OpenSSL reviewed materialization request."""

    _require_equal(request.get("format"), OPENSSL_REVIEWED_MATERIALIZATION_REQUEST_FORMAT, "format")
    _require_equal(request.get("status"), "request_draft", "status")
    _require_equal(request.get("phase"), "P8", "phase")
    _require_equal(request.get("target"), "openssl_reviewed_materialization", "target")
    _require_equal(request.get("mode"), "request_only", "mode")
    _require_non_empty_string(request.get("source_pin_digest"), "source_pin_digest")
    _require_non_empty_string(request.get("trace_contract_digest"), "trace_contract_digest")
    _require_non_empty_string(request.get("workspace_root"), "workspace_root")
    checks = _require_dict(request.get("checks"), "checks")
    for check in REQUEST_CHECKS:
        _require_equal(checks.get(check), True, f"checks.{check}")
    _require_equal(request.get("approval_required"), True, "approval_required")
    _require_equal(request.get("human_review_required"), True, "human_review_required")
    _require_equal(request.get("source_text_embedded"), False, "source_text_embedded")
    _require_equal(request.get("diff_embedded"), False, "diff_embedded")
    _require_equal(request.get("commands_embedded"), False, "commands_embedded")
    _require_equal(request.get("materialization_allowed"), False, "materialization_allowed")
    _require_equal(request.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(request.get("compile_allowed"), False, "compile_allowed")
    _require_equal(request.get("execution_allowed"), False, "execution_allowed")
    _require_equal(request.get("raw_capture_allowed"), False, "raw_capture_allowed")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLReviewedMaterializationRequestError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLReviewedMaterializationRequestError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLReviewedMaterializationRequestError(f"{name} must be {expected!r}")
