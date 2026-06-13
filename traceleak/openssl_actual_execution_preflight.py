"""OpenSSL actual execution preflight report helpers."""

from __future__ import annotations

from typing import Any

OPENSSL_ACTUAL_EXECUTION_PREFLIGHT_FORMAT = "traceleak.openssl_actual_execution_preflight.v1"
REQUIRED_PREFLIGHT_CHECKS = [
    "isolated_workspace_declared",
    "source_pin_bound",
    "trace_contract_bound",
    "redacted_trace_only",
    "approval_record_required",
    "patch_application_not_allowed",
    "compile_not_allowed",
    "execution_not_allowed",
    "raw_capture_not_allowed",
    "cleanup_plan_required",
]


class OpenSSLActualExecutionPreflightError(ValueError):
    """Raised when an OpenSSL actual execution preflight report is invalid."""


def build_openssl_actual_execution_preflight_report(
    *,
    source_pin_digest: str = "",
    trace_contract_digest: str = "",
    workspace_root: str = "",
    cleanup_plan: str = "",
) -> dict[str, Any]:
    """Build a readiness report for the future actual OpenSSL execution stage."""

    checks = {
        "isolated_workspace_declared": bool(workspace_root),
        "source_pin_bound": bool(source_pin_digest),
        "trace_contract_bound": bool(trace_contract_digest),
        "redacted_trace_only": True,
        "approval_record_required": True,
        "patch_application_not_allowed": True,
        "compile_not_allowed": True,
        "execution_not_allowed": True,
        "raw_capture_not_allowed": True,
        "cleanup_plan_required": bool(cleanup_plan),
    }
    blockers = [check for check in REQUIRED_PREFLIGHT_CHECKS if not checks[check]]
    report = {
        "format": OPENSSL_ACTUAL_EXECUTION_PREFLIGHT_FORMAT,
        "status": "readiness_report_ready",
        "phase": "P6",
        "target": "openssl_actual_execution",
        "mode": "preflight_only",
        "source_pin_digest": source_pin_digest,
        "trace_contract_digest": trace_contract_digest,
        "workspace_root": workspace_root,
        "cleanup_plan": cleanup_plan,
        "checks": checks,
        "blockers": blockers,
        "approval_required": True,
        "activation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_actual_execution_preflight_report(report)
    return report


def validate_openssl_actual_execution_preflight_report(report: dict[str, Any]) -> None:
    """Validate an OpenSSL actual execution preflight report."""

    _require_equal(report.get("format"), OPENSSL_ACTUAL_EXECUTION_PREFLIGHT_FORMAT, "format")
    _require_equal(report.get("status"), "readiness_report_ready", "status")
    _require_equal(report.get("phase"), "P6", "phase")
    _require_equal(report.get("target"), "openssl_actual_execution", "target")
    _require_equal(report.get("mode"), "preflight_only", "mode")
    _require_equal(report.get("approval_required"), True, "approval_required")
    _require_equal(report.get("activation_allowed"), False, "activation_allowed")
    _require_equal(report.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(report.get("compile_allowed"), False, "compile_allowed")
    _require_equal(report.get("execution_allowed"), False, "execution_allowed")
    _require_equal(report.get("raw_capture_allowed"), False, "raw_capture_allowed")
    checks = _require_dict(report.get("checks"), "checks")
    for check in REQUIRED_PREFLIGHT_CHECKS:
        if check not in checks:
            raise OpenSSLActualExecutionPreflightError(f"checks missing: {check}")
        if not isinstance(checks[check], bool):
            raise OpenSSLActualExecutionPreflightError(f"checks.{check} must be a bool")
    blockers = _require_string_list(report.get("blockers"), "blockers", allow_empty=True)
    unknown_blockers = sorted(set(blockers) - set(REQUIRED_PREFLIGHT_CHECKS))
    if unknown_blockers:
        raise OpenSSLActualExecutionPreflightError(
            f"blockers unknown: {', '.join(unknown_blockers)}"
        )
    expected_blockers = [check for check in REQUIRED_PREFLIGHT_CHECKS if not checks[check]]
    if blockers != expected_blockers:
        raise OpenSSLActualExecutionPreflightError("blockers must match failed checks")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLActualExecutionPreflightError(f"{name} must be an object")
    return value


def _require_string_list(value: Any, name: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise OpenSSLActualExecutionPreflightError(f"{name} must be a list")
    if not allow_empty and not value:
        raise OpenSSLActualExecutionPreflightError(f"{name} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise OpenSSLActualExecutionPreflightError(f"{name} must contain only non-empty strings")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLActualExecutionPreflightError(f"{name} must be {expected!r}")
