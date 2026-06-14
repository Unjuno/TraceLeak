import json

from scripts import run_openssl_model_sequence_metadata_sample_demo as cli
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
    build_openssl_model_sequence_metadata_sample_model_preflight,
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
        sample_id="openssl-p24-sample",
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


def write_inputs(tmp_path):
    (
        sample_manifest,
        approval_record,
        approval_gate,
        request_contract,
        output_contract,
        output_manifest,
        sample,
    ) = make_chain_and_sample()
    model_preflight = build_openssl_model_sequence_metadata_sample_model_preflight(
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    payloads = {
        "sample-contract.json": {},
        "sample-manifest.json": sample_manifest,
        "approval-record.json": approval_record,
        "approval-gate.json": approval_gate,
        "request-contract.json": request_contract,
        "output-contract.json": output_contract,
        "output-manifest.json": output_manifest,
        "sample.json": sample,
        "model-preflight.json": model_preflight,
    }
    paths = {}
    for name, payload in payloads.items():
        path = tmp_path / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths[name] = path
    return paths


def test_run_openssl_metadata_sample_demo_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    paths = write_inputs(tmp_path)
    summary = tmp_path / "summary.json"
    baseline = tmp_path / "baseline.json"
    nn = tmp_path / "nn.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_openssl_model_sequence_metadata_sample_demo",
            "--sample-contract",
            str(paths["sample-contract.json"]),
            "--sample-manifest",
            str(paths["sample-manifest.json"]),
            "--approval-record",
            str(paths["approval-record.json"]),
            "--approval-gate",
            str(paths["approval-gate.json"]),
            "--request-contract",
            str(paths["request-contract.json"]),
            "--output-contract",
            str(paths["output-contract.json"]),
            "--output-manifest",
            str(paths["output-manifest.json"]),
            "--sample",
            str(paths["sample.json"]),
            "--model-preflight",
            str(paths["model-preflight.json"]),
            "--summary-out",
            str(summary),
            "--baseline-out",
            str(baseline),
            "--nn-out",
            str(nn),
            "--epochs",
            "20",
        ],
    )

    assert cli.main() == 0
    summary_payload = json.loads(summary.read_text(encoding="utf-8"))
    baseline_payload = json.loads(baseline.read_text(encoding="utf-8"))
    nn_payload = json.loads(nn.read_text(encoding="utf-8"))
    assert summary_payload["format"] == "traceleak.openssl_model_sequence_metadata_sample_demo_result.v1"
    assert summary_payload["phase"] == "P24"
    assert summary_payload["flags"]["openssl_leakage_claim"] is False
    assert summary_payload["flags"]["baseline_result_generated"] is True
    assert summary_payload["flags"]["model_result_generated"] is True
    assert baseline_payload["result_type"] == "model_sequence_baseline"
    assert nn_payload["result_type"] == "model_sequence_nn"
    assert "not OpenSSL leakage evidence" in " ".join(nn_payload["notes"])


def test_run_openssl_metadata_sample_demo_cli_rejects_bad_preflight(tmp_path, monkeypatch) -> None:
    paths = write_inputs(tmp_path)
    bad_preflight = json.loads(paths["model-preflight.json"].read_text(encoding="utf-8"))
    bad_preflight["preflight"]["model_result_generated"] = True
    paths["model-preflight.json"].write_text(json.dumps(bad_preflight), encoding="utf-8")
    summary = tmp_path / "summary.json"
    baseline = tmp_path / "baseline.json"
    nn = tmp_path / "nn.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_openssl_model_sequence_metadata_sample_demo",
            "--sample-contract",
            str(paths["sample-contract.json"]),
            "--sample-manifest",
            str(paths["sample-manifest.json"]),
            "--approval-record",
            str(paths["approval-record.json"]),
            "--approval-gate",
            str(paths["approval-gate.json"]),
            "--request-contract",
            str(paths["request-contract.json"]),
            "--output-contract",
            str(paths["output-contract.json"]),
            "--output-manifest",
            str(paths["output-manifest.json"]),
            "--sample",
            str(paths["sample.json"]),
            "--model-preflight",
            str(paths["model-preflight.json"]),
            "--summary-out",
            str(summary),
            "--baseline-out",
            str(baseline),
            "--nn-out",
            str(nn),
        ],
    )

    assert cli.main() == 1
    assert not summary.exists()
