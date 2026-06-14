import pytest

from traceleak.openssl_actual_execution_preflight import (
    build_openssl_actual_execution_preflight_report,
)
from traceleak.openssl_isolated_execution_plan import (
    build_openssl_isolated_execution_plan,
)
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
from traceleak.openssl_model_sequence_sample_approval_gate import (
    OpenSSLModelSequenceSampleApprovalGateError,
    build_openssl_model_sequence_sample_approval_gate,
    build_openssl_model_sequence_sample_approval_record,
    validate_openssl_model_sequence_sample_approval_gate,
    validate_openssl_model_sequence_sample_approval_record,
)
from traceleak.openssl_model_sequence_sample_contract import (
    build_openssl_model_sequence_sample_contract,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    build_openssl_model_sequence_sample_manifest,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_sample_manifest() -> dict:
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
        sample_id="openssl-p18-sample",
    )
    preflight = build_openssl_model_sequence_ingestion_preflight(
        handoff_contract=handoff
    )
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
    return build_openssl_model_sequence_sample_manifest(
        sample_contract=sample_contract,
        sample_digest="sha256:sample",
    )


def test_build_sample_approval_gate_allows_request_only() -> None:
    manifest = make_sample_manifest()
    approval_record = build_openssl_model_sequence_sample_approval_record(
        sample_manifest=manifest,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )
    gate = build_openssl_model_sequence_sample_approval_gate(
        sample_manifest=manifest,
        approval_record=approval_record,
    )

    assert gate["format"] == "traceleak.openssl_model_sequence_sample_approval_gate.v1"
    assert gate["status"] == "sample_approval_gate_satisfied"
    assert gate["phase"] == "P18"
    assert gate["approval_scope"] == "sample_materialization_request_only"
    assert gate["sample_digest"] == manifest["sample_digest"]
    assert gate["sample_materialization_allowed"] is True
    assert gate["metadata_only"] is True
    assert gate["payload_free"] is True
    assert gate["sample_ready"] is False
    assert gate["model_use_enabled"] is False
    assert gate["model_training_allowed"] is False
    assert gate["runtime_action_enabled"] is False
    assert gate["payload_access_enabled"] is False


def test_openssl_model_sequence_sample_approval_record_rejects_wrong_scope() -> None:
    manifest = make_sample_manifest()
    approval_record = build_openssl_model_sequence_sample_approval_record(
        sample_manifest=manifest,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )
    approval_record["approval_scope"] = "model_training"

    with pytest.raises(
        OpenSSLModelSequenceSampleApprovalGateError,
        match="approval_scope",
    ):
        validate_openssl_model_sequence_sample_approval_record(
            approval_record=approval_record,
            sample_manifest=manifest,
        )


def test_sample_approval_record_rejects_digest_mismatch() -> None:
    manifest = make_sample_manifest()
    approval_record = build_openssl_model_sequence_sample_approval_record(
        sample_manifest=manifest,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )
    approval_record["sample_digest"] = "sha256:other-sample"

    with pytest.raises(
        OpenSSLModelSequenceSampleApprovalGateError,
        match="sample_digest",
    ):
        validate_openssl_model_sequence_sample_approval_record(
            approval_record=approval_record,
            sample_manifest=manifest,
        )


def test_sample_approval_gate_rejects_model_use_enabled() -> None:
    manifest = make_sample_manifest()
    approval_record = build_openssl_model_sequence_sample_approval_record(
        sample_manifest=manifest,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )
    gate = build_openssl_model_sequence_sample_approval_gate(
        sample_manifest=manifest,
        approval_record=approval_record,
    )
    gate["model_use_enabled"] = True

    with pytest.raises(
        OpenSSLModelSequenceSampleApprovalGateError,
        match="model_use_enabled",
    ):
        validate_openssl_model_sequence_sample_approval_gate(
            gate=gate,
            sample_manifest=manifest,
            approval_record=approval_record,
        )
