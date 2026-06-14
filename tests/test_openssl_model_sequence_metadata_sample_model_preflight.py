import pytest

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
    build_openssl_model_sequence_metadata_sample,
)
from traceleak.openssl_model_sequence_metadata_sample_model_preflight import (
    OpenSSLModelSequenceMetadataSampleModelPreflightError,
    build_openssl_model_sequence_metadata_sample_model_preflight,
    validate_openssl_model_sequence_metadata_sample_model_preflight,
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


def make_chain_and_sample() -> tuple[dict, dict, dict, dict, dict, dict, dict]:
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
        sample_id="openssl-p23-sample",
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
    sample = build_openssl_model_sequence_metadata_sample(
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        record_count=4,
    )
    return (
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
        output_manifest,
        sample,
    )


def test_build_metadata_sample_model_preflight_confirms_parser_compatibility() -> None:
    (
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
        output_manifest,
        sample,
    ) = make_chain_and_sample()
    preflight = build_openssl_model_sequence_metadata_sample_model_preflight(
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )

    assert preflight["format"] == (
        "traceleak.openssl_model_sequence_metadata_sample_model_preflight.v1"
    )
    assert preflight["status"] == "metadata_sample_model_preflight_ready"
    assert preflight["phase"] == "P23"
    assert preflight["record_count"] == 4
    assert preflight["label_name"] == "metadata_probe_bucket"
    assert preflight["label_distribution"] == {
        "metadata_even": 2,
        "metadata_odd": 2,
    }
    assert preflight["label_count"] == 2
    assert preflight["feature_count"] >= 4
    assert preflight["preflight"]["baseline_input_compatible"] is True
    assert preflight["preflight"]["nn_input_compatible"] is True
    assert preflight["preflight"]["leave_one_out_ready"] is True
    assert preflight["preflight"]["baseline_result_generated"] is False
    assert preflight["preflight"]["model_result_generated"] is False
    assert preflight["preflight"]["model_training_allowed"] is False
    assert preflight["preflight"]["runtime_action_enabled"] is False
    assert preflight["preflight"]["payload_access_enabled"] is False


def test_metadata_sample_model_preflight_rejects_model_result_generated() -> None:
    (
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
        output_manifest,
        sample,
    ) = make_chain_and_sample()
    preflight = build_openssl_model_sequence_metadata_sample_model_preflight(
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    preflight["preflight"]["model_result_generated"] = True

    with pytest.raises(
        OpenSSLModelSequenceMetadataSampleModelPreflightError,
        match="model_result_generated",
    ):
        validate_openssl_model_sequence_metadata_sample_model_preflight(
            preflight=preflight,
            sample=sample,
            output_manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )


def test_metadata_sample_model_preflight_rejects_sample_binding_mismatch() -> None:
    (
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
        output_manifest,
        sample,
    ) = make_chain_and_sample()
    preflight = build_openssl_model_sequence_metadata_sample_model_preflight(
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    preflight["sample_digest"] = "sha256:other-sample"

    with pytest.raises(
        OpenSSLModelSequenceMetadataSampleModelPreflightError,
        match="sample_digest",
    ):
        validate_openssl_model_sequence_metadata_sample_model_preflight(
            preflight=preflight,
            sample=sample,
            output_manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )


def test_metadata_sample_model_preflight_rejects_rare_label() -> None:
    (
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
        output_manifest,
        sample,
    ) = make_chain_and_sample()
    sample["records"][0]["label"] = "metadata_rare"

    with pytest.raises(Exception, match="label"):
        build_openssl_model_sequence_metadata_sample_model_preflight(
            sample=sample,
            output_manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )
