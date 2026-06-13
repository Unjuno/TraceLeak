import pytest

from traceleak.openssl_actual_execution_preflight import build_openssl_actual_execution_preflight_report
from traceleak.openssl_isolated_execution_plan import build_openssl_isolated_execution_plan
from traceleak.openssl_reviewed_materialization_request import (
    OpenSSLReviewedMaterializationRequestError,
    build_openssl_reviewed_materialization_request,
    validate_openssl_reviewed_materialization_request,
)


def make_execution_plan() -> dict:
    preflight = build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )
    return build_openssl_isolated_execution_plan(preflight_report=preflight)


def test_build_openssl_reviewed_materialization_request_is_request_only() -> None:
    request = build_openssl_reviewed_materialization_request(execution_plan=make_execution_plan())

    assert request["format"] == "traceleak.openssl_reviewed_materialization_request.v1"
    assert request["status"] == "request_draft"
    assert request["phase"] == "P8"
    assert request["mode"] == "request_only"
    assert request["approval_required"] is True
    assert request["human_review_required"] is True
    assert request["source_text_embedded"] is False
    assert request["diff_embedded"] is False
    assert request["commands_embedded"] is False
    assert request["materialization_allowed"] is False
    assert request["patch_application_allowed"] is False
    assert request["execution_allowed"] is False
    assert request["raw_capture_allowed"] is False


def test_openssl_reviewed_materialization_request_rejects_embedded_diff() -> None:
    request = build_openssl_reviewed_materialization_request(execution_plan=make_execution_plan())
    request["diff_embedded"] = True

    with pytest.raises(OpenSSLReviewedMaterializationRequestError, match="diff_embedded"):
        validate_openssl_reviewed_materialization_request(request)


def test_openssl_reviewed_materialization_request_rejects_materialization_allowed() -> None:
    request = build_openssl_reviewed_materialization_request(execution_plan=make_execution_plan())
    request["materialization_allowed"] = True

    with pytest.raises(OpenSSLReviewedMaterializationRequestError, match="materialization_allowed"):
        validate_openssl_reviewed_materialization_request(request)


def test_openssl_reviewed_materialization_request_rejects_commands_embedded() -> None:
    request = build_openssl_reviewed_materialization_request(execution_plan=make_execution_plan())
    request["commands_embedded"] = True

    with pytest.raises(OpenSSLReviewedMaterializationRequestError, match="commands_embedded"):
        validate_openssl_reviewed_materialization_request(request)
