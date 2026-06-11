import json
import subprocess
import sys


def test_extract_model_sequence_cli_writes_sequences(tmp_path) -> None:
    output_path = tmp_path / "model_sequences.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/extract_model_sequence.py",
            "--in",
            "examples/synthetic/synthetic_trace_sample.jsonl",
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["format"] == "traceleak.model_sequence.v1"
    assert payload["public_safe"] is True
    assert payload["run_count"] == 1
    record = payload["records"][0]
    assert record["run_id"] == "synthetic_000001"
    assert record["sequence"][1]["event_token"] == "branch:synthetic_leak:synthetic_keygen:secret_dependent_branch"
    assert record["sequence"][1]["redacted_value_tokens"] == ["value_redacted.branch_taken=true"]


def test_extract_model_sequence_cli_writes_counts(tmp_path) -> None:
    output_path = tmp_path / "model_sequences.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/extract_model_sequence.py",
            "--in",
            "examples/synthetic/synthetic_trace_sample.jsonl",
            "--out",
            str(output_path),
            "--counts",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    counts = payload["records"][0]["token_counts"]
    assert counts["event_type=branch"] == 1.0
    assert counts["phase=synthetic_leak"] == 2.0
    assert counts["redacted_value=value_redacted.branch_taken=true"] == 1.0


def test_extract_model_sequence_cli_can_omit_redacted_values(tmp_path) -> None:
    output_path = tmp_path / "model_sequences.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/extract_model_sequence.py",
            "--in",
            "examples/synthetic/synthetic_trace_sample.jsonl",
            "--out",
            str(output_path),
            "--no-redacted-values",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["include_redacted_values"] is False
    assert "redacted_value_tokens" not in payload["records"][0]["sequence"][1]


def test_extract_model_sequence_cli_rejects_raw_without_allow_raw(tmp_path) -> None:
    input_path = tmp_path / "raw_trace.jsonl"
    output_path = tmp_path / "model_sequences.json"
    input_path.write_text(
        json.dumps(
            {
                "run_id": "raw_000001",
                "target": "synthetic-leak",
                "target_version": "v0",
                "view": "raw",
                "events": [
                    {
                        "step": 1,
                        "phase": "raw_phase",
                        "function": "raw_fn",
                        "event_type": "assign",
                        "name": "raw_event",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/extract_model_sequence.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "not allowed for public export" in result.stderr


def test_extract_model_sequence_cli_allows_raw_when_requested(tmp_path) -> None:
    input_path = tmp_path / "raw_trace.jsonl"
    output_path = tmp_path / "model_sequences.json"
    input_path.write_text(
        json.dumps(
            {
                "run_id": "raw_000001",
                "target": "synthetic-leak",
                "target_version": "v0",
                "view": "raw",
                "events": [
                    {
                        "step": 1,
                        "phase": "raw_phase",
                        "function": "raw_fn",
                        "event_type": "assign",
                        "name": "raw_event",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/extract_model_sequence.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
            "--allow-raw",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["public_safe"] is False
    assert payload["records"][0]["view"] == "raw"
