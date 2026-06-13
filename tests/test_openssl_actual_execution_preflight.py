import pytest

from traceleak.openssl_actual_execution_preflight import (
    OpenSSLActualExecutionPreflightError,
    build_openssl_actual_execution_preflight_report,
    validate_openssl_actual_execution_preflight_report,
)


def test_build_openssl_actual_execution_preflight_report_defaults_to_blocked() -> None:
    report = build_openssl_actual_execution_preflight_report()

    assert report["format"] == "traceleak.openssl_actual_execution_preflight.v1"
    assert report["status"] == "readiness_report_ready"
    assert report["phase"] == "P6"
    assert report["mode"] == "preflight_only"
    assert report["execution_allowed"] is False
    assert report["activation_allowed"] is False
    assert report["raw_capture_allowed"] is False
    assert report["blockers"] == [
        "isolated_workspace_declared",
        "source_pin_bound",
        "trace_contract_bound",
        "cleanup_plan_required",
    ]


def test_build_openssl_actual_execution_preflight_report_can_be_blocker_free_but_not_allowed() -> None:
    report = build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )

    assert report["blockers"] == []
    assert report["execution_allowed"] is False
    assert report["compile_allowed"] is False
    assert report["patch_application_allowed"] is False
    assert report["approval_required"] is True


def test_openssl_actual_execution_preflight_rejects_execution_allowed() -> None:
    report = build_openssl_actual_execution_preflight_report()
    report["execution_allowed"] = True

    with pytest.raises(OpenSSLActualExecutionPreflightError, match="execution_allowed"):
        validate_openssl_actual_execution_preflight_report(report)


def test_openssl_actual_execution_preflight_rejects_stale_blockers() -> None:
    report = build_openssl_actual_execution_preflight_report()
    report["blockers"] = []

    with pytest.raises(OpenSSLActualExecutionPreflightError, match="blockers must match failed checks"):
        validate_openssl_actual_execution_preflight_report(report)
