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
    OpenSSLModelSequenceIngestionPreflightError,
    build_openssl_model_sequence_ingestion_preflight,
    validate_openssl_model_sequence_ingestion_preflight,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_handoff_contract() -> dict:
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
    return build_openssl_model_sequence_handoff_contract(
        materialization_manifest=manifest,
        output_contract=contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id="openssl-p12-sample",
    )


def test_build_openssl_model_sequence_ingestion_preflight_is_preflight_only() -> None:
    preflight = build_openssl_model_sequence_ingestion_preflight(
        handoff_contract=make_handoff_contract(),
    )

    assert preflight["format"] == "traceleak.openssl_model_sequence_ingestion_preflight.v1"
    assert preflight["status"] == "preflight_ready"
    assert preflight["phase"] == "P13"
    assert preflight["mode"] == "preflight_only"
    assert preflight["feature_namespace"] == "openssl.materialization.redacted"
    assert preflight["sample_id"] == "openssl-p12-sample"
    assert preflight["blockers"] == []
    assert all(preflight["checks"].values())
    assert preflight["model_sequence_ingestion_allowed"] is False
    assert preflight["model_training_allowed"] is False
    assert preflight["execution_allowed"] is False
    assert preflight["raw_capture_allowed"] is False


def test_openssl_model_sequence_ingestion_preflight_rejects_ingestion_allowed() -> None:
    preflight = build_openssl_model_sequence_ingestion_preflight(
        handoff_contract=make_handoff_contract(),
    )
    preflight["model_sequence_ingestion_allowed"] = True

    with pytest.raises(OpenSSLModelSequenceIngestionPreflightError, match="model_sequence"):
        validate_openssl_model_sequence_ingestion_preflight(preflight)


def test_openssl_model_sequence_ingestion_preflight_rejects_stale_blockers() -> None:
    preflight = build_openssl_model_sequence_ingestion_preflight(
        handoff_contract=make_handoff_contract(),
    )
    preflight["checks"]["no_commands"] = False

    with pytest.raises(OpenSSLModelSequenceIngestionPreflightError, match="blockers"):
        validate_openssl_model_sequence_ingestion_preflight(preflight)
