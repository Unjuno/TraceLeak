import json

from scripts import validate_openssl_model_sequence_sample_materialization_output_contract as cli
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
from traceleak.openssl_model_sequence_sample_materialization_output_contract import (
    build_openssl_model_sequence_sample_materialization_output_contract,
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
    materialization_gate = build_openssl_materialization_approval_gate(
        reviewed_request=request,
        approval_record=record,
    )
    base_output_contract = build_openssl_materialization_output_contract(
        approval_gate=materialization_gate,
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
        sample_id="openssl-p20-sample",
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
    return (
        sample_contract,
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
    )


def test_validate_sample_materialization_output_contract_cli_accepts_valid_chain(
    tmp_path,
    monkeypatch,
) -> None:
    (
        sample_contract,
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
    ) = make_chain()
    sample_contract_path = tmp_path / "sample-contract.json"
    sample_manifest_path = tmp_path / "sample-manifest.json"
    approval_record_path = tmp_path / "approval-record.json"
    approval_gate_path = tmp_path / "approval-gate.json"
    request_contract_path = tmp_path / "request-contract.json"
    output_contract_path = tmp_path / "output-contract.json"
    sample_contract_path.write_text(json.dumps(sample_contract), encoding="utf-8")
    sample_manifest_path.write_text(json.dumps(sample_manifest), encoding="utf-8")
    approval_record_path.write_text(json.dumps(approval_record), encoding="utf-8")
    approval_gate_path.write_text(json.dumps(approval_gate), encoding="utf-8")
    request_contract_path.write_text(json.dumps(request_contract), encoding="utf-8")
    output_contract_path.write_text(json.dumps(output_contract), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_model_sequence_sample_materialization_output_contract",
            "--sample-contract",
            str(sample_contract_path),
            "--sample-manifest",
            str(sample_manifest_path),
            "--approval-record",
            str(approval_record_path),
            "--approval-gate",
            str(approval_gate_path),
            "--request-contract",
            str(request_contract_path),
            "--output-contract",
            str(output_contract_path),
        ],
    )

    assert cli.main() == 0


def test_validate_sample_materialization_output_contract_cli_rejects_mismatch(
    tmp_path,
    monkeypatch,
) -> None:
    (
        sample_contract,
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
    ) = make_chain()
    output_contract["sample_digest"] = "sha256:other-sample"
    sample_contract_path = tmp_path / "sample-contract.json"
    sample_manifest_path = tmp_path / "sample-manifest.json"
    approval_record_path = tmp_path / "approval-record.json"
    approval_gate_path = tmp_path / "approval-gate.json"
    request_contract_path = tmp_path / "request-contract.json"
    output_contract_path = tmp_path / "output-contract.json"
    sample_contract_path.write_text(json.dumps(sample_contract), encoding="utf-8")
    sample_manifest_path.write_text(json.dumps(sample_manifest), encoding="utf-8")
    approval_record_path.write_text(json.dumps(approval_record), encoding="utf-8")
    approval_gate_path.write_text(json.dumps(approval_gate), encoding="utf-8")
    request_contract_path.write_text(json.dumps(request_contract), encoding="utf-8")
    output_contract_path.write_text(json.dumps(output_contract), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_model_sequence_sample_materialization_output_contract",
            "--sample-contract",
            str(sample_contract_path),
            "--sample-manifest",
            str(sample_manifest_path),
            "--approval-record",
            str(approval_record_path),
            "--approval-gate",
            str(approval_gate_path),
            "--request-contract",
            str(request_contract_path),
            "--output-contract",
            str(output_contract_path),
        ],
    )

    assert cli.main() == 1
