import pytest

from traceleak.openssl_actual_execution_preflight import build_openssl_actual_execution_preflight_report
from traceleak.openssl_isolated_execution_plan import build_openssl_isolated_execution_plan
from traceleak.openssl_materialization_approval_gate import (
    build_openssl_materialization_approval_gate,
    build_openssl_materialization_approval_record,
)
from traceleak.openssl_materialization_output_contract import (
    OpenSSLMaterializationOutputContractError,
    build_openssl_materialization_output_contract,
    validate_openssl_materialization_output_contract,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_approval_gate() -> dict:
    preflight = build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )
    plan = build_openssl_isolated_execution_plan(preflight_report=preflight)
    request = build_openssl_reviewed_materialization_request(execution_plan=plan)
    record = build_openssl_materialization_approval_record(
        reviewed_request=request,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )
    return build_openssl_materialization_approval_gate(
        reviewed_request=request,
        approval_record=record,
    )


def test_build_openssl_materialization_output_contract_is_metadata_only() -> None:
    contract = build_openssl_materialization_output_contract(
        approval_gate=make_approval_gate(),
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )

    assert contract["format"] == "traceleak.openssl_materialization_output_contract.v1"
    assert contract["status"] == "output_contract_ready"
    assert contract["phase"] == "P10"
    assert contract["mode"] == "contract_only"
    assert contract["output_generated"] is False
    assert contract["output_schema"]["digest_required"] is True
    assert contract["output_schema"]["manifest_required"] is True
    assert contract["output_schema"]["redacted_metadata_only"] is True
    assert contract["output_schema"]["source_text_embedded"] is False
    assert contract["output_schema"]["diff_embedded"] is False
    assert contract["output_schema"]["commands_embedded"] is False
    assert contract["output_schema"]["build_output_embedded"] is False
    assert contract["output_schema"]["execution_output_embedded"] is False
    assert contract["output_schema"]["raw_capture_embedded"] is False
    assert contract["patch_application_allowed"] is False
    assert contract["compile_allowed"] is False
    assert contract["execution_allowed"] is False
    assert contract["raw_capture_allowed"] is False


def test_openssl_materialization_output_contract_rejects_generated_output() -> None:
    contract = build_openssl_materialization_output_contract(
        approval_gate=make_approval_gate(),
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )
    contract["output_generated"] = True

    with pytest.raises(OpenSSLMaterializationOutputContractError, match="output_generated"):
        validate_openssl_materialization_output_contract(contract)


def test_openssl_materialization_output_contract_rejects_command_embedding() -> None:
    contract = build_openssl_materialization_output_contract(
        approval_gate=make_approval_gate(),
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )
    contract["output_schema"]["commands_embedded"] = True

    with pytest.raises(OpenSSLMaterializationOutputContractError, match="commands_embedded"):
        validate_openssl_materialization_output_contract(contract)
