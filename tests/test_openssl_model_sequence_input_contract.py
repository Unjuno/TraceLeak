import pytest

from traceleak.openssl_actual_execution_preflight import build_openssl_actual_execution_preflight_report
from traceleak.openssl_isolated_execution_plan import build_openssl_isolated_execution_plan
from traceleak.openssl_materialization_approval_gate import (
    build_openssl_materialization_approval_gate,
    build_openssl_materialization_approval_record,
)
from traceleak.openssl_materialization_output_contract import (
    build_openssl_materialization_output_contract,
)
from traceleak.openssl_materialization_output_manifest import (
    build_openssl_materialization_output_manifest,
)
from traceleak.openssl_model_sequence_handoff_contract import (
    build_openssl_model_sequence_handoff_contract,
)
from traceleak.openssl_model_sequence_ingestion_preflight import (
    build_openssl_model_sequence_ingestion_preflight,
)
from traceleak.openssl_model_sequence_input_contract import (
    OpenSSLModelSequenceInputContractError,
    build_openssl_model_sequence_input_contract,
    validate_openssl_model_sequence_input_contract,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_ingestion_preflight() -> dict:
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
    gate = build_openssl_materialization_approval_gate(
        reviewed_request=request,
        approval_record=record,
    )
    contract = build_openssl_materialization_output_contract(
        approval_gate=gate,
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )
    manifest = build_openssl_materialization_output_manifest(
        output_contract=contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=manifest,
        output_contract=contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id="openssl-p14-sample",
    )
    return build_openssl_model_sequence_ingestion_preflight(handoff_contract=handoff)


def test_build_openssl_model_sequence_input_contract_is_contract_only() -> None:
    contract = build_openssl_model_sequence_input_contract(
        ingestion_preflight=make_ingestion_preflight(),
        output_sample_path="artifacts/openssl-model-sequence-input.json",
    )

    assert contract["format"] == "traceleak.openssl_model_sequence_input_contract.v1"
    assert contract["status"] == "input_contract_ready"
    assert contract["phase"] == "P14"
    assert contract["mode"] == "contract_only"
    assert contract["feature_namespace"] == "openssl.materialization.redacted"
    assert contract["sample_id"] == "openssl-p14-sample"
    assert contract["input_schema"]["metadata_only"] is True
    assert contract["input_schema"]["payload_free"] is True
    assert contract["input_ready"] is False
    assert contract["model_use_enabled"] is False


def test_openssl_model_sequence_input_contract_rejects_model_use_enabled() -> None:
    contract = build_openssl_model_sequence_input_contract(
        ingestion_preflight=make_ingestion_preflight(),
        output_sample_path="artifacts/openssl-model-sequence-input.json",
    )
    contract["model_use_enabled"] = True

    with pytest.raises(OpenSSLModelSequenceInputContractError, match="model_use_enabled"):
        validate_openssl_model_sequence_input_contract(contract)


def test_openssl_model_sequence_input_contract_rejects_payload_not_free() -> None:
    contract = build_openssl_model_sequence_input_contract(
        ingestion_preflight=make_ingestion_preflight(),
        output_sample_path="artifacts/openssl-model-sequence-input.json",
    )
    contract["input_schema"]["payload_free"] = False

    with pytest.raises(OpenSSLModelSequenceInputContractError, match="payload_free"):
        validate_openssl_model_sequence_input_contract(contract)
