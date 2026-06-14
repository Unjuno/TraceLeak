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
    build_openssl_model_sequence_input_manifest,
)
from traceleak.openssl_model_sequence_sample_contract import (
    build_openssl_model_sequence_sample_contract,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    OpenSSLModelSequenceSampleManifestError,
    build_openssl_model_sequence_sample_manifest,
    validate_openssl_model_sequence_sample_manifest,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_sample_contract() -> dict:
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
        sample_id="openssl-p17-sample",
    )
    preflight = build_openssl_model_sequence_ingestion_preflight(handoff_contract=handoff)
    input_contract = build_openssl_model_sequence_input_contract(
        ingestion_preflight=preflight,
        output_sample_path="artifacts/openssl-model-sequence-input.json",
    )
    input_manifest = build_openssl_model_sequence_input_manifest(
        input_contract=input_contract,
        input_digest="sha256:input",
    )
    return build_openssl_model_sequence_sample_contract(
        input_manifest=input_manifest,
        input_contract=input_contract,
        feature_fields=["artifact_count", "namespace_id"],
        label_fields=["label"],
        metadata_fields=["sample_id", "input_digest"],
    )


def test_build_openssl_model_sequence_sample_manifest_binds_fields() -> None:
    contract = make_sample_contract()
    manifest = build_openssl_model_sequence_sample_manifest(
        sample_contract=contract,
        sample_digest="sha256:sample",
    )

    assert manifest["format"] == "traceleak.openssl_model_sequence_sample_manifest.v1"
    assert manifest["status"] == "sample_manifest_ready"
    assert manifest["phase"] == "P17"
    assert manifest["mode"] == "metadata_only"
    assert manifest["sample_contract_format"] == contract["format"]
    assert manifest["input_digest"] == contract["input_digest"]
    assert manifest["sample_digest"] == "sha256:sample"
    assert manifest["feature_fields"] == contract["feature_fields"]
    assert manifest["label_fields"] == contract["label_fields"]
    assert manifest["metadata_fields"] == contract["metadata_fields"]
    assert manifest["manifest_schema"]["metadata_only"] is True
    assert manifest["manifest_schema"]["payload_free"] is True
    assert manifest["sample_ready"] is False
    assert manifest["model_use_enabled"] is False


def test_openssl_model_sequence_sample_manifest_rejects_field_mismatch() -> None:
    contract = make_sample_contract()
    manifest = build_openssl_model_sequence_sample_manifest(
        sample_contract=contract,
        sample_digest="sha256:sample",
    )
    manifest["feature_fields"] = ["other_field"]

    with pytest.raises(OpenSSLModelSequenceSampleManifestError, match="feature_fields"):
        validate_openssl_model_sequence_sample_manifest(
            manifest=manifest,
            sample_contract=contract,
        )


def test_openssl_model_sequence_sample_manifest_rejects_model_use_enabled() -> None:
    contract = make_sample_contract()
    manifest = build_openssl_model_sequence_sample_manifest(
        sample_contract=contract,
        sample_digest="sha256:sample",
    )
    manifest["model_use_enabled"] = True

    with pytest.raises(OpenSSLModelSequenceSampleManifestError, match="model_use_enabled"):
        validate_openssl_model_sequence_sample_manifest(
            manifest=manifest,
            sample_contract=contract,
        )
