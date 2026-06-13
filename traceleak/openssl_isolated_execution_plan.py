"""OpenSSL isolated execution plan helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_actual_execution_preflight import (
    validate_openssl_actual_execution_preflight_report,
)

OPENSSL_ISOLATED_EXECUTION_PLAN_FORMAT = "traceleak.openssl_isolated_execution_plan.v1"
PLANNED_EXECUTION_STEPS = [
    "prepare_isolated_workspace",
    "verify_source_pin",
    "materialize_reviewed_patch",
    "build_openssl",
    "run_negative_control",
    "run_redacted_trace",
    "validate_trace_artifact",
    "cleanup_workspace",
]


class OpenSSLIsolatedExecutionPlanError(ValueError):
    """Raised when an OpenSSL isolated execution plan is invalid."""


def build_openssl_isolated_execution_plan(
    *,
    preflight_report: dict[str, Any],
) -> dict[str, Any]:
    """Build a non-executable plan for future isolated OpenSSL execution."""

    validate_openssl_actual_execution_preflight_report(preflight_report)
    if preflight_report["blockers"]:
        raise OpenSSLIsolatedExecutionPlanError("preflight_report must be blocker-free")
    plan = {
        "format": OPENSSL_ISOLATED_EXECUTION_PLAN_FORMAT,
        "status": "planned_not_executable",
        "phase": "P7",
        "target": "openssl_isolated_execution",
        "mode": "plan_only",
        "source_pin_digest": preflight_report["source_pin_digest"],
        "trace_contract_digest": preflight_report["trace_contract_digest"],
        "workspace_root": preflight_report["workspace_root"],
        "cleanup_plan": preflight_report["cleanup_plan"],
        "steps": [
            {
                "name": step,
                "status": "planned",
                "command_materialized": False,
                "result_captured": False,
            }
            for step in PLANNED_EXECUTION_STEPS
        ],
        "approval_required": True,
        "activation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_isolated_execution_plan(plan)
    return plan


def validate_openssl_isolated_execution_plan(plan: dict[str, Any]) -> None:
    """Validate a non-executable isolated OpenSSL execution plan."""

    _require_equal(plan.get("format"), OPENSSL_ISOLATED_EXECUTION_PLAN_FORMAT, "format")
    _require_equal(plan.get("status"), "planned_not_executable", "status")
    _require_equal(plan.get("phase"), "P7", "phase")
    _require_equal(plan.get("target"), "openssl_isolated_execution", "target")
    _require_equal(plan.get("mode"), "plan_only", "mode")
    _require_non_empty_string(plan.get("source_pin_digest"), "source_pin_digest")
    _require_non_empty_string(plan.get("trace_contract_digest"), "trace_contract_digest")
    _require_non_empty_string(plan.get("workspace_root"), "workspace_root")
    _require_non_empty_string(plan.get("cleanup_plan"), "cleanup_plan")
    _require_equal(plan.get("approval_required"), True, "approval_required")
    _require_equal(plan.get("activation_allowed"), False, "activation_allowed")
    _require_equal(plan.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(plan.get("compile_allowed"), False, "compile_allowed")
    _require_equal(plan.get("execution_allowed"), False, "execution_allowed")
    _require_equal(plan.get("raw_capture_allowed"), False, "raw_capture_allowed")
    steps = _require_list(plan.get("steps"), "steps")
    names = []
    for index, step in enumerate(steps):
        record = _require_dict(step, f"steps[{index}]")
        names.append(record.get("name"))
        _require_equal(record.get("status"), "planned", f"steps[{index}].status")
        _require_equal(
            record.get("command_materialized"),
            False,
            f"steps[{index}].command_materialized",
        )
        _require_equal(record.get("result_captured"), False, f"steps[{index}].result_captured")
    if names != PLANNED_EXECUTION_STEPS:
        raise OpenSSLIsolatedExecutionPlanError("steps must match the planned execution sequence")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLIsolatedExecutionPlanError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise OpenSSLIsolatedExecutionPlanError(f"{name} must be a non-empty list")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLIsolatedExecutionPlanError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLIsolatedExecutionPlanError(f"{name} must be {expected!r}")
