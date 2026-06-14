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
    build_openssl_model_sequence_input_contract,
)
from traceleak.openssl_model_sequence_input_manifest import (
    OpenSSLModelSequenceInputManifestError,
    build_openssl_model_sequence_input_manifest,
    validate_openssl_model_sequence_input_manifest,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_input_contract() -> dict:
    base = build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )
    plan = build_openssl_isolated_execution_plan(preflight_report=base)
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
    output_contract = build_openssl_materialization_output_contract(
        approval_gate=gate,
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )
    output_manifest = build_openssl_materialization_output_manifest(
        output_contract=output_contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=output_manifest,
        output_contract=output_contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id="openssl-p15-sample",
    )
    preflight = build_openssl_model_sequence_ingestion_preflight(handoff_contract=handoff)
    return build_openssl_model_sequence_input_contract(
        ingestion_preflight=preflight,
        output_sample_path="artifacts/openssl-model-sequence-input.json",
    )


def test_build_openssl_model_sequence_input_manifest_is_metadata_only() -> None:
    contract = make_input_contract()
    manifest = build_openssl_model_sequence_input_manifest(
        input_contract=contract,
        input_digest="sha256:input",
    )

    assert manifest["format"] == "traceleak.openssl_model_sequence_input_manifest.v1"
    assert manifest["status"] == "input_manifest_ready"
    assert manifest["phase"] == "P15"
    assert manifest["mode"] == "metadata_only"
    assert manifest["contract_format"] == contract["format"]
    assert manifest["artifact_digests"] == contract["artifact_digests"]
    assert manifest["feature_namespace"] == contract["feature_namespace"]
    assert manifest["sample_id"] == contract["sample_id"]
    assert manifest["input_digest"] == "sha256:input"
    assert manifest["manifest_schema"]["metadata_only"] is True
    assert manifest["manifest_schema"]["payload_free"] is True
    assert manifest["input_ready"] is False
    assert manifest["model_use_enabled"] is False


def test_openssl_model_sequence_input_manifest_rejects_contract_mismatch() -> None:
    contract = make_input_contract()
    manifest = build_openssl_model_sequence_input_manifest(
        input_contract=contract,
        input_digest="sha256:input",
    )
    manifest["sample_id"] = "other-sample"

    with pytest.raises(OpenSSLModelSequenceInputManifestError, match="sample_id"):
        validate_openssl_model_sequence_input_manifest(
            manifest=manifest,
            input_contract=contract,
        )


def test_openssl_model_sequence_input_manifest_rejects_model_use_enabled() -> None:
    contract = make_input_contract()
    manifest = build_openssl_model_sequence_input_manifest(
        input_contract=contract,
        input_digest="sha256:input",
    )
    manifest["model_use_enabled"] = True

    with pytest.raises(OpenSSLModelSequenceInputManifestError, match="model_use_enabled"):
        validate_openssl_model_sequence_input_manifest(
            manifest=manifest,
            input_contract=contract,
        )
