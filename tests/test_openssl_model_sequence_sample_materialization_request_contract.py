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
    build_openssl_model_sequence_sample_approval_gate,
    build_openssl_model_sequence_sample_approval_record,
)
from traceleak.openssl_model_sequence_sample_contract import (
    build_openssl_model_sequence_sample_contract,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    build_openssl_model_sequence_sample_manifest,
)
from traceleak.openssl_model_sequence_sample_materialization_request_contract import (
    OpenSSLModelSequenceSampleMaterializationRequestContractError,
    build_openssl_model_sequence_sample_materialization_request_contract,
    validate_openssl_model_sequence_sample_materialization_request_contract,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_manifest_record_gate() -> tuple[dict, dict, dict]:
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
        sample_id="openssl-p19-sample",
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
    return sample_manifest, approval_record, approval_gate


def test_build_sample_materialization_request_contract_is_request_only() -> None:
    manifest, approval_record, approval_gate = make_manifest_record_gate()
    request_contract = build_openssl_model_sequence_sample_materialization_request_contract(
        sample_manifest=manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        planned_sample_path="artifacts/openssl-model-sequence-sample.json",
    )

    assert request_contract["format"] == (
        "traceleak.openssl_model_sequence_sample_materialization_request_contract.v1"
    )
    assert request_contract["status"] == "sample_materialization_request_contract_ready"
    assert request_contract["phase"] == "P19"
    assert request_contract["mode"] == "request_contract_only"
    assert request_contract["sample_digest"] == manifest["sample_digest"]
    assert request_contract["planned_sample_path"] == (
        "artifacts/openssl-model-sequence-sample.json"
    )
    assert request_contract["request_only"] is True
    assert request_contract["metadata_only"] is True
    assert request_contract["payload_free"] is True
    assert request_contract["sample_materialization_allowed"] is True
    assert request_contract["sample_ready"] is False
    assert request_contract["model_use_enabled"] is False
    assert request_contract["model_training_allowed"] is False
    assert request_contract["runtime_action_enabled"] is False
    assert request_contract["payload_access_enabled"] is False


def test_sample_materialization_request_contract_rejects_digest_mismatch() -> None:
    manifest, approval_record, approval_gate = make_manifest_record_gate()
    request_contract = build_openssl_model_sequence_sample_materialization_request_contract(
        sample_manifest=manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        planned_sample_path="artifacts/openssl-model-sequence-sample.json",
    )
    request_contract["sample_digest"] = "sha256:other-sample"

    with pytest.raises(
        OpenSSLModelSequenceSampleMaterializationRequestContractError,
        match="sample_digest",
    ):
        validate_openssl_model_sequence_sample_materialization_request_contract(
            request_contract=request_contract,
            sample_manifest=manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
        )


def test_sample_materialization_request_contract_rejects_payload_access_enabled() -> None:
    manifest, approval_record, approval_gate = make_manifest_record_gate()
    request_contract = build_openssl_model_sequence_sample_materialization_request_contract(
        sample_manifest=manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        planned_sample_path="artifacts/openssl-model-sequence-sample.json",
    )
    request_contract["payload_access_enabled"] = True

    with pytest.raises(
        OpenSSLModelSequenceSampleMaterializationRequestContractError,
        match="payload_access_enabled",
    ):
        validate_openssl_model_sequence_sample_materialization_request_contract(
            request_contract=request_contract,
            sample_manifest=manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
        )


def test_sample_materialization_request_contract_rejects_empty_planned_path() -> None:
    manifest, approval_record, approval_gate = make_manifest_record_gate()
    request_contract = build_openssl_model_sequence_sample_materialization_request_contract(
        sample_manifest=manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        planned_sample_path="artifacts/openssl-model-sequence-sample.json",
    )
    request_contract["planned_sample_path"] = ""

    with pytest.raises(
        OpenSSLModelSequenceSampleMaterializationRequestContractError,
        match="planned_sample_path",
    ):
        validate_openssl_model_sequence_sample_materialization_request_contract(
            request_contract=request_contract,
            sample_manifest=manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
        )
