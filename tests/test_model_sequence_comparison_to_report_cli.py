# ruff: noqa: I001

import json
import subprocess
import sys


COMPARISON = {
    "result_type": "model_sequence_nn_vs_baseline",
    "target": "synthetic-count-pattern",
    "view": "redacted",
    "label_name": "secret_bucket",
    "example_count": 16,
    "baseline": {
        "leave_one_out_majority_accuracy": 0.0,
        "leave_one_out_nearest_neighbor_accuracy": 0.25,
    },
    "neural": {
        "model_name": "sparse-softmax-model-sequence-nn",
        "backend": "python-standard-library",
        "leave_one_out_accuracy": 1.0,
        "DeltaH": 1.0,
        "top_attributions": [
            {
                "group_id": "event_token=loop:candidate_balance:synthetic_keygen:refine_round",
                "group_type": "model_sequence_token",
                "score": 0.75,
                "evidence": ["sparse_softmax_weight_separation"],
            }
        ],
    },
    "delta": {"accuracy_vs_nearest_neighbor": 0.75},
    "interpretation": "neural_better",
    "notes": ["sample note"],
}


CONTROL = {
    **COMPARISON,
    "target": "synthetic-count-pattern-control-001",
    "label_name": "control_bucket_seed_001",
    "neural": {
        **COMPARISON["neural"],
        "leave_one_out_accuracy": 0.0,
        "DeltaH": 0.0,
    },
    "delta": {"accuracy_vs_nearest_neighbor": -0.25},
    "interpretation": "baseline_better",
}


def test_model_sequence_comparison_to_report_cli_writes_markdown(tmp_path) -> None:
    input_path = tmp_path / "comparison.json"
    output_path = tmp_path / "comparison.md"
    input_path.write_text(json.dumps(COMPARISON), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_sequence_comparison_to_report.py",
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
    markdown = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Model Sequence NN Comparison Report" in markdown
    assert "Top NN Attributions" in markdown
    assert "neural_better" in markdown
    assert "controls_missing" in markdown


def test_model_sequence_comparison_to_report_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "comparison.json"
    output_path = tmp_path / "comparison_report.json"
    input_path.write_text(json.dumps(COMPARISON), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_sequence_comparison_to_report.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["report_type"] == "model_sequence_nn_comparison_report"
    assert payload["delta_accuracy"] == 0.75
    assert payload["evidence_status"] == "controls_missing"
    assert payload["top_attributions"]


def test_model_sequence_comparison_to_report_cli_accepts_controls(tmp_path) -> None:
    input_path = tmp_path / "comparison.json"
    control_path = tmp_path / "control.json"
    output_path = tmp_path / "comparison.md"
    input_path.write_text(json.dumps(COMPARISON), encoding="utf-8")
    control_path.write_text(json.dumps(CONTROL), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_sequence_comparison_to_report.py",
            "--in",
            str(input_path),
            "--control",
            str(control_path),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert "Control Summary" in markdown
    assert "control_pass" in markdown
    assert "candidate_signal_control_checked" in markdown


def test_model_sequence_comparison_to_report_cli_rejects_missing_input(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_sequence_comparison_to_report.py",
            "--in",
            str(tmp_path / "missing.json"),
            "--out",
            str(tmp_path / "comparison.md"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "comparison file not found" in result.stderr
