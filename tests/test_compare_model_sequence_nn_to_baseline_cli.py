import json
import subprocess
import sys


def test_compare_model_sequence_nn_to_baseline_cli_writes_json(tmp_path) -> None:
    output_path = tmp_path / "model_sequence_nn_comparison.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/compare_model_sequence_nn_to_baseline.py",
            "--in",
            "examples/synthetic/model_sequence_nn_hard_sample.json",
            "--out",
            str(output_path),
            "--epochs",
            "80",
            "--learning-rate",
            "0.8",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["result_type"] == "model_sequence_nn_vs_baseline"
    assert payload["example_count"] == 8


def test_compare_model_sequence_nn_to_baseline_cli_rejects_missing_input(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/compare_model_sequence_nn_to_baseline.py",
            "--in",
            str(tmp_path / "missing.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "input file not found" in result.stderr
