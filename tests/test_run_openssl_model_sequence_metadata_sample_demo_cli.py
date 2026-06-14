import json

from scripts import run_openssl_model_sequence_metadata_sample_demo as cli
from traceleak.openssl_model_sequence_metadata_sample_model_preflight import (
    build_openssl_model_sequence_metadata_sample_model_preflight,
)
from tests.test_openssl_model_sequence_metadata_sample_model_preflight import (
    make_chain_and_sample,
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
