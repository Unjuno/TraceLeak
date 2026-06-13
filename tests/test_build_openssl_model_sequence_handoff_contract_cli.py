import json

from scripts import build_openssl_model_sequence_handoff_contract as cli
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
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_contract_and_manifest() -> tuple[dict, dict]:
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
    return contract, manifest


def test_build_openssl_model_sequence_handoff_contract_cli_writes_contract(
    tmp_path,
    monkeypatch,
) -> None:
    contract, manifest = make_contract_and_manifest()
    contract_path = tmp_path / "contract.json"
    manifest_path = tmp_path / "manifest.json"
    out = tmp_path / "handoff.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_openssl_model_sequence_handoff_contract",
            "--contract",
            str(contract_path),
            "--manifest",
            str(manifest_path),
            "--feature-namespace",
            "openssl.materialization.redacted",
            "--sample-id",
            "openssl-p12-sample",
            "--out",
            str(out),
        ],
    )

    assert cli.main() == 0

    handoff = json.loads(out.read_text(encoding="utf-8"))
    assert handoff["format"] == "traceleak.openssl_model_sequence_handoff_contract.v1"
    assert handoff["status"] == "handoff_contract_ready"
    assert handoff["phase"] == "P12"
    assert handoff["mode"] == "contract_only"
    assert handoff["feature_namespace"] == "openssl.materialization.redacted"
    assert handoff["sample_id"] == "openssl-p12-sample"
    assert handoff["handoff_schema"]["redacted_metadata_only"] is True
    assert handoff["handoff_schema"]["commands_embedded"] is False
    assert handoff["model_sequence_ingestion_allowed"] is False
    assert handoff["model_training_allowed"] is False
