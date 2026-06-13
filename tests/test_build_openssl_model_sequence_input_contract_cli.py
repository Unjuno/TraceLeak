import json

from scripts import build_openssl_model_sequence_input_contract as cli
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
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_preflight() -> dict:
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
    contract = build_openssl_materialization_output_contract(
        approval_gate=gate,
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )
    manifest = build_openssl_materialization_output_manifest(
        output_contract=contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=manifest,
        output_contract=contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id="openssl-p14-sample",
    )
    return build_openssl_model_sequence_ingestion_preflight(handoff_contract=handoff)


def test_build_openssl_model_sequence_input_contract_cli_writes_contract(tmp_path, monkeypatch) -> None:
    preflight_path = tmp_path / "preflight.json"
    out = tmp_path / "input-contract.json"
    preflight_path.write_text(json.dumps(make_preflight()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_openssl_model_sequence_input_contract",
            "--preflight",
            str(preflight_path),
            "--output-sample-path",
            "artifacts/openssl-model-sequence-input.json",
            "--out",
            str(out),
        ],
    )

    assert cli.main() == 0

    contract = json.loads(out.read_text(encoding="utf-8"))
    assert contract["format"] == "traceleak.openssl_model_sequence_input_contract.v1"
    assert contract["phase"] == "P14"
    assert contract["mode"] == "contract_only"
    assert contract["input_schema"]["metadata_only"] is True
    assert contract["input_schema"]["payload_free"] is True
    assert contract["input_ready"] is False
    assert contract["model_use_enabled"] is False
