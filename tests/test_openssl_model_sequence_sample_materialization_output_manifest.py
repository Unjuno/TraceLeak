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
    OpenSSLModelSequenceSampleMaterializationOutputManifestError,
    build_openssl_model_sequence_sample_materialization_output_manifest,
    validate_openssl_model_sequence_sample_materialization_output_manifest,
)
from traceleak.openssl_model_sequence_sample_materialization_request_contract import (
    build_openssl_model_sequence_sample_materialization_request_contract,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_chain() -> tuple[dict, dict, dict, dict, dict]:
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
        sample_id="openssl-p21-sample",
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
        planned_sample_path="artifacts/openssl-model-sequence-sample.json",
    )
    output_contract = build_openssl_model_sequence_sample_materialization_output_contract(
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        output_manifest_path="artifacts/openssl-model-sequence-sample-output-manifest.json",
    )
    return sample_manifest, approval_record, approval_gate, request_contract, output_contract


def test_build_sample_materialization_output_manifest_is_metadata_only() -> None:
    manifest, approval_record, approval_gate, request_contract, output_contract = make_chain()
    output_manifest = build_openssl_model_sequence_sample_materialization_output_manifest(
        output_contract=output_contract,
        sample_manifest=manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        artifact_digests={"sample": "sha256:sample"},
    )

    assert output_manifest["format"] == (
        "traceleak.openssl_model_sequence_sample_materialization_output_manifest.v1"
    )
    assert output_manifest["status"] == "sample_materialization_output_manifest_ready"
    assert output_manifest["phase"] == "P21"
    assert output_manifest["mode"] == "metadata_only"
    assert output_manifest["sample_digest"] == manifest["sample_digest"]
    assert output_manifest["planned_sample_path"] == output_contract["planned_sample_path"]
    assert output_manifest["output_manifest_path"] == output_contract["output_manifest_path"]
    assert output_manifest["artifact_digests"] == {"sample": "sha256:sample"}
    assert output_manifest["metadata"]["output_contract_bound"] is True
    assert output_manifest["metadata"]["request_contract_bound"] is True
    assert output_manifest["metadata"]["digest_recorded"] is True
    assert output_manifest["metadata"]["metadata_only"] is True
    assert output_manifest["metadata"]["payload_free"] is True
    assert output_manifest["metadata"]["sample_artifact_generated"] is False
    assert output_manifest["metadata"]["model_use_enabled"] is False
    assert output_manifest["metadata"]["model_training_allowed"] is False
    assert output_manifest["metadata"]["runtime_action_enabled"] is False
    assert output_manifest["metadata"]["payload_access_enabled"] is False


def test_sample_materialization_output_manifest_rejects_empty_artifact_digests() -> None:
    manifest, approval_record, approval_gate, request_contract, output_contract = make_chain()
    output_manifest = build_openssl_model_sequence_sample_materialization_output_manifest(
        output_contract=output_contract,
        sample_manifest=manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        artifact_digests={"sample": "sha256:sample"},
    )
    output_manifest["artifact_digests"] = {}

    with pytest.raises(
        OpenSSLModelSequenceSampleMaterializationOutputManifestError,
        match="artifact_digests",
    ):
        validate_openssl_model_sequence_sample_materialization_output_manifest(
            manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )


def test_sample_materialization_output_manifest_rejects_sample_artifact_generated() -> None:
    manifest, approval_record, approval_gate, request_contract, output_contract = make_chain()
    output_manifest = build_openssl_model_sequence_sample_materialization_output_manifest(
        output_contract=output_contract,
        sample_manifest=manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        artifact_digests={"sample": "sha256:sample"},
    )
    output_manifest["metadata"]["sample_artifact_generated"] = True

    with pytest.raises(
        OpenSSLModelSequenceSampleMaterializationOutputManifestError,
        match="sample_artifact_generated",
    ):
        validate_openssl_model_sequence_sample_materialization_output_manifest(
            manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )


def test_sample_materialization_output_manifest_rejects_output_contract_mismatch() -> None:
    manifest, approval_record, approval_gate, request_contract, output_contract = make_chain()
    output_manifest = build_openssl_model_sequence_sample_materialization_output_manifest(
        output_contract=output_contract,
        sample_manifest=manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        artifact_digests={"sample": "sha256:sample"},
    )
    output_manifest["output_manifest_path"] = "artifacts/other-manifest.json"

    with pytest.raises(
        OpenSSLModelSequenceSampleMaterializationOutputManifestError,
        match="output_manifest_path",
    ):
        validate_openssl_model_sequence_sample_materialization_output_manifest(
            manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )
