import json
from pathlib import Path

import pytest

from scripts import build_openssl_trace_sample
from traceleak.openssl_trace_acceptance import validate_openssl_trace_sample_acceptance
from traceleak.openssl_trace_contract import load_openssl_trace_contract
from traceleak.openssl_trace_sample_builder import (
    OpenSSLTraceSampleBuilderError,
    build_openssl_model_sequence_sample,
    load_redacted_event_runs,
)

CONTRACT_PATH = Path("examples/openssl_trace_contract/openssl_rsa_keygen_trace_contract_sample.json")


def contract() -> dict:
    return load_openssl_trace_contract(CONTRACT_PATH)


def redacted_run(run_id: str, label: int, loop_count: int) -> dict:
    c = contract()
    return {
        "run_id": run_id,
        "target": c["target"],
        "target_version": c["target_version"],
        "view": "redacted",
        "labels_lab_only": {"rsa_keygen_attempt_bucket": label},
        "metadata": {
            "source_pin": c["source_pin"],
            "build_id": c["build_id"],
            "trace_collection_mode": "redacted",
            "raw_secret_captured": False,
            "public_safe": True,
        },
        "events": [
            {
                "step": 0,
                "phase": "candidate_generation",
                "function": "ossl_rsa_keygen",
                "event_type": "phase",
                "name": "candidate_filter",
                "file": "crypto/rsa/rsa_gen.c",
                "line": 100,
            },
            {
                "step": 1,
                "phase": "candidate_generation",
                "function": "ossl_rsa_keygen",
                "event_type": "loop",
                "name": "bn_prime_trial_division",
                "file": "crypto/rsa/rsa_gen.c",
                "line": 101,
                "value_redacted": {"count_bucket": loop_count},
            },
            {
                "step": 2,
                "phase": "candidate_generation",
                "function": "ossl_rsa_keygen",
                "event_type": "branch",
                "name": "candidate_rejected",
                "file": "crypto/rsa/rsa_gen.c",
                "line": 102,
            },
        ],
    }


def write_jsonl(path: Path, runs: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(run, sort_keys=True) for run in runs) + "\n", encoding="utf-8")


def test_builds_acceptance_valid_model_sequence_sample_from_redacted_runs() -> None:
    runs = [
        redacted_run("openssl_redacted_run_000001", 0, 3),
        redacted_run("openssl_redacted_run_000002", 1, 5),
    ]

    sample = build_openssl_model_sequence_sample(
        contract=contract(),
        runs=runs,
        input_name="redacted-runs.jsonl",
    )

    assert sample["format"] == "traceleak.model_sequence.v1"
    assert sample["actual_trace_derived"] is True
    assert sample["trace_collection_mode"] == "redacted"
    assert sample["raw_secret_captured"] is False
    assert sample["include_redacted_values"] is False
    assert sample["label_name"] == "rsa_keygen_attempt_bucket"
    assert sample["run_count"] == 2
    assert "redacted_value=value_redacted.count_bucket=3" not in sample["records"][0]["token_counts"]
    validate_openssl_trace_sample_acceptance(contract(), sample)


def test_load_redacted_event_runs_reads_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "runs.jsonl"
    write_jsonl(path, [redacted_run("openssl_redacted_run_000001", 0, 3)])

    runs = load_redacted_event_runs(path)

    assert len(runs) == 1
    assert runs[0]["run_id"] == "openssl_redacted_run_000001"


def test_builder_rejects_raw_view() -> None:
    run = redacted_run("openssl_raw_run", 0, 3)
    run["view"] = "raw"

    with pytest.raises(OpenSSLTraceSampleBuilderError, match="view"):
        build_openssl_model_sequence_sample(
            contract=contract(),
            runs=[run],
            input_name="raw-runs.jsonl",
        )


def test_builder_rejects_source_pin_mismatch() -> None:
    run = redacted_run("openssl_bad_source_pin", 0, 3)
    run["metadata"]["source_pin"] = "sha256:other"

    with pytest.raises(OpenSSLTraceSampleBuilderError, match="source_pin"):
        build_openssl_model_sequence_sample(
            contract=contract(),
            runs=[run],
            input_name="bad-source-runs.jsonl",
        )


def test_builder_rejects_raw_secret_capture_metadata() -> None:
    run = redacted_run("openssl_raw_secret_capture", 0, 3)
    run["metadata"]["raw_secret_captured"] = True

    with pytest.raises(OpenSSLTraceSampleBuilderError, match="raw_secret_captured"):
        build_openssl_model_sequence_sample(
            contract=contract(),
            runs=[run],
            input_name="raw-secret-runs.jsonl",
        )


def test_builder_rejects_missing_lab_label() -> None:
    run = redacted_run("openssl_missing_label", 0, 3)
    run["labels_lab_only"] = {}

    with pytest.raises(OpenSSLTraceSampleBuilderError, match="rsa_keygen_attempt_bucket"):
        build_openssl_model_sequence_sample(
            contract=contract(),
            runs=[run],
            input_name="missing-label-runs.jsonl",
        )


def test_build_openssl_trace_sample_cli_writes_acceptance_valid_sample(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    input_path = tmp_path / "runs.jsonl"
    output_path = tmp_path / "sample.json"
    write_jsonl(
        input_path,
        [
            redacted_run("openssl_redacted_run_000001", 0, 3),
            redacted_run("openssl_redacted_run_000002", 1, 5),
        ],
    )
    old_parse = build_openssl_trace_sample.parse_args
    build_openssl_trace_sample.parse_args = lambda: type(
        "Args",
        (),
        {
            "contract": CONTRACT_PATH,
            "input_path": input_path,
            "output_path": output_path,
            "label_key": None,
        },
    )()
    try:
        assert build_openssl_trace_sample.main() == 0
    finally:
        build_openssl_trace_sample.parse_args = old_parse

    sample = json.loads(output_path.read_text(encoding="utf-8"))
    validate_openssl_trace_sample_acceptance(contract(), sample)
    assert sample["run_count"] == 2
    assert "wrote OpenSSL model-sequence sample" in capsys.readouterr().out
