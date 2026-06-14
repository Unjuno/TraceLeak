import json

from scripts import validate_openssl_model_sequence_sample_approval_gate as cli
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
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_contract_manifest_record_gate() -> tuple[dict, dict, dict, dict]:
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
    output_contract = build_openssl_materialization_output_contract(
        approval_gate=materialization_gate,
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
    return sample_contract, sample_manifest, approval_record, approval_gate


def test_validate_sample_approval_gate_cli_accepts_valid_chain(
    tmp_path,
    monkeypatch,
) -> None:
    contract, manifest, approval_record, gate = make_contract_manifest_record_gate()
    contract_path = tmp_path / "contract.json"
    manifest_path = tmp_path / "manifest.json"
    record_path = tmp_path / "approval-record.json"
    gate_path = tmp_path / "gate.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    record_path.write_text(json.dumps(approval_record), encoding="utf-8")
    gate_path.write_text(json.dumps(gate), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_model_sequence_sample_approval_gate",
            "--contract",
            str(contract_path),
            "--manifest",
            str(manifest_path),
            "--approval-record",
            str(record_path),
            "--gate",
            str(gate_path),
        ],
    )

    assert cli.main() == 0


def test_validate_sample_approval_gate_cli_rejects_gate_mismatch(
    tmp_path,
    monkeypatch,
) -> None:
    contract, manifest, approval_record, gate = make_contract_manifest_record_gate()
    gate["sample_digest"] = "sha256:other-sample"
    contract_path = tmp_path / "contract.json"
    manifest_path = tmp_path / "manifest.json"
    record_path = tmp_path / "approval-record.json"
    gate_path = tmp_path / "gate.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    record_path.write_text(json.dumps(approval_record), encoding="utf-8")
    gate_path.write_text(json.dumps(gate), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_model_sequence_sample_approval_gate",
            "--contract",
            str(contract_path),
            "--manifest",
            str(manifest_path),
            "--approval-record",
            str(record_path),
            "--gate",
            str(gate_path),
        ],
    )

    assert cli.main() == 1
