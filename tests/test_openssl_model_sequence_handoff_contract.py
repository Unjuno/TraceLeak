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
    OpenSSLModelSequenceHandoffContractError,
    build_openssl_model_sequence_handoff_contract,
    validate_openssl_model_sequence_handoff_contract,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_contract_and_manifest() -> tuple[dict, dict]:
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
    return contract, manifest


def test_build_openssl_model_sequence_handoff_contract_is_contract_only() -> None:
    contract, manifest = make_contract_and_manifest()
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=manifest,
        output_contract=contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id="openssl-p12-sample",
    )

    assert handoff["format"] == "traceleak.openssl_model_sequence_handoff_contract.v1"
    assert handoff["status"] == "handoff_contract_ready"
    assert handoff["phase"] == "P12"
    assert handoff["mode"] == "contract_only"
    assert handoff["manifest_format"] == manifest["format"]
    assert handoff["contract_format"] == contract["format"]
    assert handoff["artifact_digests"] == manifest["artifact_digests"]
    assert handoff["feature_namespace"] == "openssl.materialization.redacted"
    assert handoff["sample_id"] == "openssl-p12-sample"
    assert handoff["handoff_schema"]["redacted_metadata_only"] is True
    assert handoff["handoff_schema"]["source_text_embedded"] is False
    assert handoff["handoff_schema"]["diff_embedded"] is False
    assert handoff["handoff_schema"]["commands_embedded"] is False
    assert handoff["handoff_schema"]["raw_capture_embedded"] is False
    assert handoff["handoff_generated"] is False
    assert handoff["model_sequence_ingestion_allowed"] is False
    assert handoff["model_training_allowed"] is False
    assert handoff["execution_allowed"] is False
    assert handoff["raw_capture_allowed"] is False


def test_openssl_model_sequence_handoff_contract_rejects_ingestion_allowed() -> None:
    contract, manifest = make_contract_and_manifest()
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=manifest,
        output_contract=contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id="openssl-p12-sample",
    )
    handoff["model_sequence_ingestion_allowed"] = True

    with pytest.raises(OpenSSLModelSequenceHandoffContractError, match="model_sequence"):
        validate_openssl_model_sequence_handoff_contract(handoff)


def test_openssl_model_sequence_handoff_contract_rejects_payload_embedding() -> None:
    contract, manifest = make_contract_and_manifest()
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=manifest,
        output_contract=contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id="openssl-p12-sample",
    )
    handoff["handoff_schema"]["commands_embedded"] = True

    with pytest.raises(OpenSSLModelSequenceHandoffContractError, match="commands_embedded"):
        validate_openssl_model_sequence_handoff_contract(handoff)
