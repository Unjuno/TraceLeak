import json

from scripts import build_openssl_model_sequence_sample_contract as cli
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
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_input_pair() -> tuple[dict, dict]:
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
        sample_id="openssl-p16-sample",
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
    return input_contract, input_manifest


def test_build_openssl_model_sequence_sample_contract_cli_writes_contract(tmp_path, monkeypatch) -> None:
    input_contract, input_manifest = make_input_pair()
    contract_path = tmp_path / "input-contract.json"
    manifest_path = tmp_path / "input-manifest.json"
    out = tmp_path / "sample-contract.json"
    contract_path.write_text(json.dumps(input_contract), encoding="utf-8")
    manifest_path.write_text(json.dumps(input_manifest), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_openssl_model_sequence_sample_contract",
            "--contract",
            str(contract_path),
            "--manifest",
            str(manifest_path),
            "--feature-field",
            "artifact_count",
            "--feature-field",
            "namespace_id",
            "--label-field",
            "label",
            "--metadata-field",
            "sample_id",
            "--metadata-field",
            "input_digest",
            "--out",
            str(out),
        ],
    )

    assert cli.main() == 0

    contract = json.loads(out.read_text(encoding="utf-8"))
    assert contract["format"] == "traceleak.openssl_model_sequence_sample_contract.v1"
    assert contract["phase"] == "P16"
    assert contract["mode"] == "contract_only"
    assert contract["feature_fields"] == ["artifact_count", "namespace_id"]
    assert contract["label_fields"] == ["label"]
    assert contract["sample_schema"]["metadata_only"] is True
    assert contract["sample_schema"]["payload_free"] is True
    assert contract["sample_ready"] is False
    assert contract["model_use_enabled"] is False
