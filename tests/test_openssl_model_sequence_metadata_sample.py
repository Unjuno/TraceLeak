import pytest

from traceleak.model_sequence_nn import parse_model_sequence_nn_vectors
from traceleak.openssl_actual_execution_preflight import (
    build_openssl_actual_execution_preflight_report,
)
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
from traceleak.openssl_model_sequence_metadata_sample import (
    OpenSSLModelSequenceMetadataSampleError,
    build_openssl_model_sequence_metadata_sample,
    validate_openssl_model_sequence_metadata_sample,
)
from traceleak.openssl_model_sequence_sample_approval_gate import (
    build_openssl_model_sequence_sample_approval_gate,
    build_openssl_model_sequence_sample_approval_record,
)
from traceleak.openssl_model_sequence_sample_contract import (
    build_openssl_model_sequence_sample_contract,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    build_openssl_model_sequence_sample_manifest,
)
from traceleak.openssl_model_sequence_sample_materialization_output_contract import (
    build_openssl_model_sequence_sample_materialization_output_contract,
)
from traceleak.openssl_model_sequence_sample_materialization_output_manifest import (
    build_openssl_model_sequence_sample_materialization_output_manifest,
)
from traceleak.openssl_model_sequence_sample_materialization_request_contract import (
    build_openssl_model_sequence_sample_materialization_request_contract,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_chain() -> tuple[dict, dict, dict, dict, dict, dict]:
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
    base_output_contract = build_openssl_materialization_output_contract(
        approval_gate=gate,
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )
    base_output_manifest = build_openssl_materialization_output_manifest(
        output_contract=base_output_contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=base_output_manifest,
        output_contract=base_output_contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id="openssl-p22-sample",
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
    sample_contract = build_openssl_model_sequence_sample_contract(
        input_manifest=input_manifest,
        input_contract=input_contract,
        feature_fields=["artifact_count", "namespace_id"],
        label_fields=["label"],
        metadata_fields=["sample_id", "input_digest"],
    )
    sample_manifest = build_openssl_model_sequence_sample_manifest(
        sample_contract=sample_contract,
        sample_digest="sha256:sample",
    )
    approval_record = build_openssl_model_sequence_sample_approval_record(
        sample_manifest=sample_manifest,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )
    approval_gate = build_openssl_model_sequence_sample_approval_gate(
        sample_manifest=sample_manifest,
        approval_record=approval_record,
    )
    request_contract = build_openssl_model_sequence_sample_materialization_request_contract(
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        planned_sample_path="artifacts/openssl-model-sequence-metadata-sample.json",
    )
    output_contract = build_openssl_model_sequence_sample_materialization_output_contract(
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        output_manifest_path="artifacts/openssl-model-sequence-metadata-sample-output-manifest.json",
    )
    output_manifest = build_openssl_model_sequence_sample_materialization_output_manifest(
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        artifact_digests={"sample": "sha256:sample"},
    )
    return sample_manifest, approval_record, approval_gate, request_contract, output_contract, output_manifest


def test_build_openssl_model_sequence_metadata_sample_is_model_sequence_compatible() -> None:
    sample_manifest, approval_record, approval_gate, request_contract, output_contract, output_manifest = make_chain()
    sample = build_openssl_model_sequence_metadata_sample(
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        record_count=4,
    )

    assert sample["format"] == "traceleak.model_sequence.v1"
    assert sample["artifact_format"] == "traceleak.openssl_model_sequence_metadata_sample.v1"
    assert sample["run_count"] == 4
    assert sample["public_safe"] is True
    assert sample["include_counts"] is True
    assert sample["include_redacted_values"] is False
    assert sample["sample_metadata"]["phase"] == "P22"
    assert sample["sample_metadata"]["metadata_only"] is True
    assert sample["sample_metadata"]["payload_free"] is True
    assert sample["sample_metadata"]["sample_artifact_generated"] is True
    assert sample["sample_metadata"]["model_use_enabled"] is False
    assert sample["sample_metadata"]["model_training_allowed"] is False
    assert sample["sample_metadata"]["runtime_action_enabled"] is False
    assert sample["sample_metadata"]["payload_access_enabled"] is False
    vectors = parse_model_sequence_nn_vectors(sample)
    assert len(vectors) == 4
    assert {vector.label for vector in vectors} == {"metadata_even", "metadata_odd"}


def test_openssl_model_sequence_metadata_sample_rejects_odd_record_count() -> None:
    sample_manifest, approval_record, approval_gate, request_contract, output_contract, output_manifest = make_chain()

    with pytest.raises(OpenSSLModelSequenceMetadataSampleError, match="record_count"):
        build_openssl_model_sequence_metadata_sample(
            output_manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
            record_count=5,
        )


def test_openssl_model_sequence_metadata_sample_rejects_forbidden_payload_field() -> None:
    sample_manifest, approval_record, approval_gate, request_contract, output_contract, output_manifest = make_chain()
    sample = build_openssl_model_sequence_metadata_sample(
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        record_count=4,
    )
    sample["payload"] = {"forbidden": True}

    with pytest.raises(OpenSSLModelSequenceMetadataSampleError, match="payload"):
        validate_openssl_model_sequence_metadata_sample(
            sample=sample,
            output_manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )


def test_openssl_model_sequence_metadata_sample_rejects_training_enabled() -> None:
    sample_manifest, approval_record, approval_gate, request_contract, output_contract, output_manifest = make_chain()
    sample = build_openssl_model_sequence_metadata_sample(
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        record_count=4,
    )
    sample["sample_metadata"]["model_training_allowed"] = True

    with pytest.raises(OpenSSLModelSequenceMetadataSampleError, match="model_training_allowed"):
        validate_openssl_model_sequence_metadata_sample(
            sample=sample,
            output_manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )
