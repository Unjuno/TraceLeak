import json
import subprocess
import sys


def test_evaluate_model_sequence_baseline_cli_prints_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_model_sequence_baseline.py",
            "--in",
            "examples/synthetic/model_sequence_baseline_sample.json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result_type"] == "model_sequence_baseline"
    assert payload["baselines"]["leave_one_out_nearest_neighbor_accuracy"] == 1.0


def test_evaluate_model_sequence_baseline_cli_writes_json(tmp_path) -> None:
    output_path = tmp_path / "baseline_result.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_model_sequence_baseline.py",
            "--in",
            "examples/synthetic/model_sequence_baseline_sample.json",
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["target"] == "synthetic-leak"
    assert payload["view"] == "redacted"
    assert payload["label_distribution"] == {"0": 2, "1": 2}


def test_model_vs_sequence_baseline_comparison_sample_renders(tmp_path) -> None:
    output_path = tmp_path / "model_vs_sequence_baseline.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/comparison_to_report.py",
            "--in",
            "examples/synthetic/model_vs_sequence_baseline_comparison_sample.json",
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Comparison Report" in text
    assert "model_vs_sequence_baseline" in text
    assert "sequence_nearest_neighbor_baseline" in text
