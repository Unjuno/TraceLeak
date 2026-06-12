# ruff: noqa: I001

import json
import subprocess
import sys

from traceleak.model_sequence_comparison import compare_model_sequence_nn_to_baseline


def test_build_toy_rsa_like_model_sequence_sample_cli_writes_trace_and_sample(tmp_path) -> None:
    sample_path = tmp_path / "toy_trace_derived_model_sequence.json"
    trace_path = tmp_path / "toy_trace_derived.jsonl"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_toy_rsa_like_model_sequence_sample.py",
            "--out",
            str(sample_path),
            "--trace-out",
            str(trace_path),
            "--runs",
            "8",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert sample_path.exists()
    assert trace_path.exists()

    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    trace_lines = [line for line in trace_path.read_text(encoding="utf-8").splitlines() if line]
    assert sample["format"] == "traceleak.model_sequence.v1"
    assert sample["run_count"] == 8
    assert sample["include_counts"] is True
    assert sample["contains_lab_only_labels"] is True
    assert sample["label_name"] == "toy_accept_attempt_bucket"
    assert sample["label_proxy_filter"]["enabled"] is True
    assert len(sample["records"]) == 8
    assert len(trace_lines) == 8
    assert all("label" in record for record in sample["records"])
    assert all("token_counts" in record for record in sample["records"])
    assert not any(
        "attempt_bucket" in token
        for record in sample["records"]
        for token in record["token_counts"]
    )

    comparison = compare_model_sequence_nn_to_baseline(sample, epochs=20, learning_rate=0.8)
    assert comparison["result_type"] == "model_sequence_nn_vs_baseline"
    assert comparison["target"] == "toy-rsa-like-trace-derived"


def test_build_toy_rsa_like_model_sequence_sample_cli_can_omit_redacted_values(tmp_path) -> None:
    sample_path = tmp_path / "toy_trace_derived_no_values.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_toy_rsa_like_model_sequence_sample.py",
            "--out",
            str(sample_path),
            "--runs",
            "4",
            "--no-redacted-values",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    assert sample["include_redacted_values"] is False
    assert not any(
        token.startswith("redacted_value=")
        for record in sample["records"]
        for token in record["token_counts"]
    )


def test_build_toy_rsa_like_model_sequence_sample_cli_rejects_non_positive_runs(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_toy_rsa_like_model_sequence_sample.py",
            "--out",
            str(tmp_path / "sample.json"),
            "--runs",
            "0",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--runs must be positive" in result.stderr
