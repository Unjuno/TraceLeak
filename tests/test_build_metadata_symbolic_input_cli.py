import json

from scripts import build_metadata_symbolic_input as cli
from traceleak.openssl_derived_metadata_adapter import adapt_openssl_derived_metadata_to_model_sequence
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate


def test_build_metadata_symbolic_input_cli_writes_default_input(tmp_path, monkeypatch) -> None:
    out_path = tmp_path / "symbolic-metadata.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_metadata_symbolic_input",
            "--out",
            str(out_path),
        ],
    )

    assert cli.main() == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["format"] == "traceleak.openssl_derived_metadata_input.v1"
    assert payload["authoring_phase"] == "P80"
    assert len(payload["records"]) == 4


def test_build_metadata_symbolic_input_cli_output_adapts(tmp_path, monkeypatch) -> None:
    out_path = tmp_path / "symbolic-metadata.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_metadata_symbolic_input",
            "--out",
            str(out_path),
            "--label-name",
            "bucket_label",
        ],
    )

    assert cli.main() == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    gate = build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )
    sample = adapt_openssl_derived_metadata_to_model_sequence(
        metadata_input=payload,
        runtime_gate=gate,
    )
    assert sample["label_name"] == "bucket_label"
    assert sample["run_count"] == 4


def test_build_metadata_symbolic_input_cli_rejects_empty_source_pin(tmp_path, monkeypatch) -> None:
    out_path = tmp_path / "symbolic-metadata.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_metadata_symbolic_input",
            "--out",
            str(out_path),
            "--source-pin-digest",
            "",
        ],
    )

    assert cli.main() == 1
    assert not out_path.exists()
