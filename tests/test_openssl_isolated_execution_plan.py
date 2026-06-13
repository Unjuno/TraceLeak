import pytest

from traceleak.openssl_actual_execution_preflight import (
    build_openssl_actual_execution_preflight_report,
)
from traceleak.openssl_isolated_execution_plan import (
    PLANNED_EXECUTION_STEPS,
    OpenSSLIsolatedExecutionPlanError,
    build_openssl_isolated_execution_plan,
    validate_openssl_isolated_execution_plan,
)


def make_blocker_free_preflight() -> dict:
    return build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )


def test_build_openssl_isolated_execution_plan_is_plan_only() -> None:
    plan = build_openssl_isolated_execution_plan(preflight_report=make_blocker_free_preflight())

    assert plan["format"] == "traceleak.openssl_isolated_execution_plan.v1"
    assert plan["status"] == "planned_not_executable"
    assert plan["phase"] == "P7"
    assert plan["mode"] == "plan_only"
    assert [step["name"] for step in plan["steps"]] == PLANNED_EXECUTION_STEPS
    assert {step["status"] for step in plan["steps"]} == {"planned"}
    assert {step["command_materialized"] for step in plan["steps"]} == {False}
    assert {step["result_captured"] for step in plan["steps"]} == {False}
    assert plan["execution_allowed"] is False
    assert plan["compile_allowed"] is False
    assert plan["patch_application_allowed"] is False
    assert plan["raw_capture_allowed"] is False


def test_openssl_isolated_execution_plan_rejects_blocked_preflight() -> None:
    with pytest.raises(OpenSSLIsolatedExecutionPlanError, match="blocker-free"):
        build_openssl_isolated_execution_plan(
            preflight_report=build_openssl_actual_execution_preflight_report()
        )


def test_openssl_isolated_execution_plan_rejects_execution_allowed() -> None:
    plan = build_openssl_isolated_execution_plan(preflight_report=make_blocker_free_preflight())
    plan["execution_allowed"] = True

    with pytest.raises(OpenSSLIsolatedExecutionPlanError, match="execution_allowed"):
        validate_openssl_isolated_execution_plan(plan)


def test_openssl_isolated_execution_plan_rejects_materialized_command() -> None:
    plan = build_openssl_isolated_execution_plan(preflight_report=make_blocker_free_preflight())
    plan["steps"][0]["command_materialized"] = True

    with pytest.raises(OpenSSLIsolatedExecutionPlanError, match="command_materialized"):
        validate_openssl_isolated_execution_plan(plan)
