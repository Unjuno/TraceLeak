import json

from scripts import validate_openssl_model_sequence_input_manifest as cli
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


def make_contract_and_manifest() -> tuple[dict, dict]:
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
        sample_id="openssl-p15-sample",
    )
    preflight = build_openssl_model_sequence_ingestion_preflight(handoff_contract=handoff)
    contract = build_openssl_model_sequence_input_contract(
        ingestion_preflight=preflight,
        output_sample_path="artifacts/openssl-model-sequence-input.json",
    )
    manifest = build_openssl_model_sequence_input_manifest(
        input_contract=contract,
        input_digest="sha256:input",
    )
    return contract, manifest


def test_validate_openssl_model_sequence_input_manifest_cli_accepts_valid_pair(
    tmp_path,
    monkeypatch,
) -> None:
    contract, manifest = make_contract_and_manifest()
    contract_path = tmp_path / "contract.json"
    manifest_path = tmp_path / "manifest.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_model_sequence_input_manifest",
            "--contract",
            str(contract_path),
            "--manifest",
            str(manifest_path),
        ],
    )

    assert cli.main() == 0


def test_validate_openssl_model_sequence_input_manifest_cli_rejects_mismatch(
    tmp_path,
    monkeypatch,
) -> None:
    contract, manifest = make_contract_and_manifest()
    manifest["feature_namespace"] = "other.namespace"
    contract_path = tmp_path / "contract.json"
    manifest_path = tmp_path / "manifest.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_model_sequence_input_manifest",
            "--contract",
            str(contract_path),
            "--manifest",
            str(manifest_path),
        ],
    )

    assert cli.main() == 1
