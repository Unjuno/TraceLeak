import pytest

from traceleak.openssl_actual_execution_preflight import build_openssl_actual_execution_preflight_report
from traceleak.openssl_isolated_execution_plan import build_openssl_isolated_execution_plan
from traceleak.openssl_materialization_approval_gate import (
    OpenSSLMaterializationApprovalGateError,
    build_openssl_materialization_approval_gate,
    build_openssl_materialization_approval_record,
    validate_openssl_materialization_approval_record,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_reviewed_request() -> dict:
    preflight = build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )
    plan = build_openssl_isolated_execution_plan(preflight_report=preflight)
    return build_openssl_reviewed_materialization_request(execution_plan=plan)


def make_approval_record(reviewed_request: dict) -> dict:
    return build_openssl_materialization_approval_record(
        reviewed_request=reviewed_request,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )


def test_build_openssl_materialization_approval_gate_accepts_reviewed_request() -> None:
    reviewed_request = make_reviewed_request()
    approval_record = make_approval_record(reviewed_request)

    gate = build_openssl_materialization_approval_gate(
        reviewed_request=reviewed_request,
        approval_record=approval_record,
    )

    assert gate["format"] == "traceleak.openssl_materialization_approval_gate.v1"
    assert gate["status"] == "approval_gate_satisfied"
    assert gate["phase"] == "P9"
    assert gate["mode"] == "approval_gate_only"
    assert gate["approval_record_accepted"] is True
    assert gate["materialization_request_approved"] is True
    assert gate["materialization_allowed"] is True
    assert gate["patch_application_allowed"] is False
    assert gate["compile_allowed"] is False
    assert gate["execution_allowed"] is False
    assert gate["raw_capture_allowed"] is False


def test_openssl_materialization_approval_record_rejects_wrong_scope() -> None:
    reviewed_request = make_reviewed_request()
    approval_record = make_approval_record(reviewed_request)
    approval_record["approval_scope"] = "wrong_scope"

    with pytest.raises(OpenSSLMaterializationApprovalGateError, match="approval_scope"):
        validate_openssl_materialization_approval_record(
            approval_record=approval_record,
            reviewed_request=reviewed_request,
        )


def test_openssl_materialization_approval_record_rejects_mismatched_source_pin() -> None:
    reviewed_request = make_reviewed_request()
    approval_record = make_approval_record(reviewed_request)
    approval_record["source_pin_digest"] = "sha256:other-source-pin"

    with pytest.raises(OpenSSLMaterializationApprovalGateError, match="source_pin_digest"):
        validate_openssl_materialization_approval_record(
            approval_record=approval_record,
            reviewed_request=reviewed_request,
        )
