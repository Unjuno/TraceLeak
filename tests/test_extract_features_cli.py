import csv
import json
import subprocess
import sys


def sample_trace_line() -> str:
    return json.dumps(
        {
            "run_id": "synthetic_000001",
            "target": "synthetic-example",
            "target_version": "v0",
            "view": "redacted",
            "events": [
                {
                    "step": 1,
                    "phase": "synthetic_phase",
                    "function": "synthetic_fn",
                    "event_type": "branch",
                    "name": "example_branch_event",
                    "value_redacted": {"count": 2},
                }
            ],
        }
    )


def test_extract_features_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "trace.jsonl"
    output_path = tmp_path / "features.json"
    input_path.write_text(sample_trace_line() + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/extract_features.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload[0]["run_id"] == "synthetic_000001"
    assert payload[0]["features"]["run.view=redacted"] == 1.0


def test_extract_features_cli_writes_csv(tmp_path) -> None:
    input_path = tmp_path / "trace.jsonl"
    output_path = tmp_path / "features.csv"
    input_path.write_text(sample_trace_line() + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/extract_features.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
            "--format",
            "csv",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    with output_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[0][0] == "run_id"
    assert rows[1][0] == "synthetic_000001"


def test_extract_features_cli_rejects_empty_file(tmp_path) -> None:
    input_path = tmp_path / "empty.jsonl"
    output_path = tmp_path / "features.json"
    input_path.write_text("", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/extract_features.py",
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
    assert "no runs found" in result.stderr
