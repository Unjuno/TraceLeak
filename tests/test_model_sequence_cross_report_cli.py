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
        "leave_one_out_nearest_neighbor_accuracy": 0.4375,
    },
    "neural": {
        "model_name": "sparse-softmax-model-sequence-nn",
        "backend": "python-standard-library",
        "leave_one_out_accuracy": 1.0,
        "DeltaH": 1.0,
        "top_attributions": [
            {
                "group_id": "event_token=loop:synthetic-count-pattern:ratio_a",
                "group_type": "model_sequence_token",
                "score": 10.0,
                "evidence": ["sparse_softmax_weight_separation"],
            }
        ],
    },
    "delta": {"accuracy_vs_nearest_neighbor": 0.5625},
    "interpretation": "neural_better",
    "notes": ["sample note"],
}


CONTROL = {
    **COMPARISON,
    "target": "synthetic-count-pattern-control",
    "label_name": "control_bucket",
    "neural": {
        **COMPARISON["neural"],
        "leave_one_out_accuracy": 0.0,
        "DeltaH": 0.0,
    },
    "delta": {"accuracy_vs_nearest_neighbor": -0.4375},
    "interpretation": "baseline_better",
}


def test_model_sequence_cross_report_cli_writes_markdown(tmp_path) -> None:
    comparison_path = tmp_path / "comparison.json"
    control_path = tmp_path / "control.json"
    output_path = tmp_path / "cross_report.md"
    comparison_path.write_text(json.dumps(COMPARISON), encoding="utf-8")
    control_path.write_text(json.dumps(CONTROL), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_sequence_cross_report.py",
            "--entry",
            f"synthetic={comparison_path}",
            "--control",
            f"synthetic={control_path}",
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Model Sequence Cross Report" in markdown
    assert "synthetic-count-pattern" in markdown
    assert "control_pass" in markdown


def test_model_sequence_cross_report_cli_writes_json(tmp_path) -> None:
    comparison_path = tmp_path / "comparison.json"
    output_path = tmp_path / "cross_report.json"
    comparison_path.write_text(json.dumps(COMPARISON), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_sequence_cross_report.py",
            "--entry",
            f"synthetic={comparison_path}",
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
    assert payload["report_type"] == "model_sequence_cross_report"
    assert payload["rows"][0]["control_status"] == "not_provided"


def test_model_sequence_cross_report_cli_rejects_missing_entry(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_sequence_cross_report.py",
            "--out",
            str(tmp_path / "cross_report.md"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "at least one --entry" in result.stderr
