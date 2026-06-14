import json

from scripts import adapt_openssl_derived_metadata as cli
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate


def make_metadata_input() -> dict:
    return {
        "format": "traceleak.openssl_derived_metadata_input.v1",
        "source_pin_digest": "sha256:source-pin",
        "target_decision": "constant_time_helper_misuse_path",
        "metadata_only": True,
        "payload_free": True,
        "label_name": "metadata_bucket",
        "records": [
            {
                "run_id": "r0",
                "source_region_token": "ct_helper_family_a",
                "transition_token": "branch_symbolic_a",
                "label": "bucket_a",
            },
            {
                "run_id": "r1",
                "source_region_token": "ct_helper_family_b",
                "transition_token": "branch_symbolic_b",
                "label": "bucket_b",
            },
        ],
    }


def test_adapt_openssl_derived_metadata_cli_writes_model_sequence(tmp_path, monkeypatch) -> None:
    metadata_path = tmp_path / "metadata.json"
    gate_path = tmp_path / "runtime-gate.json"
    out_path = tmp_path / "model-sequence.json"
    metadata_path.write_text(json.dumps(make_metadata_input()), encoding="utf-8")
    gate_path.write_text(
        json.dumps(
            build_openssl_runtime_transition_gate(
                reviewer="reviewer",
                reviewed_at="2026-06-14T00:00:00Z",
            )
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "adapt_openssl_derived_metadata",
            "--metadata",
            str(metadata_path),
            "--runtime-gate",
            str(gate_path),
            "--out",
            str(out_path),
        ],
    )

    assert cli.main() == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["format"] == "traceleak.model_sequence.v1"
    assert payload["artifact_format"] == "traceleak.openssl_derived_metadata_model_sequence.v1"


def test_adapt_openssl_derived_metadata_cli_rejects_forbidden_field(tmp_path, monkeypatch) -> None:
    metadata = make_metadata_input()
    metadata["records"][0]["raw_capture"] = "not allowed"
    metadata_path = tmp_path / "metadata.json"
    gate_path = tmp_path / "runtime-gate.json"
    out_path = tmp_path / "model-sequence.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    gate_path.write_text(
        json.dumps(
            build_openssl_runtime_transition_gate(
                reviewer="reviewer",
                reviewed_at="2026-06-14T00:00:00Z",
            )
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "adapt_openssl_derived_metadata",
            "--metadata",
            str(metadata_path),
            "--runtime-gate",
            str(gate_path),
            "--out",
            str(out_path),
        ],
    )

    assert cli.main() == 1
    assert not out_path.exists()
