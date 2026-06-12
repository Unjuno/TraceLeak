from traceleak.model_sequence_comparison import compare_model_sequence_nn_to_baseline
from traceleak.model_sequence_comparison_reporting import (
    model_sequence_comparison_report_dict,
    model_sequence_comparison_report_markdown,
)


def comparison_result() -> dict:
    return {
        "result_type": "model_sequence_nn_vs_baseline",
        "target": "synthetic-count-pattern",
        "view": "redacted",
        "label_name": "secret_bucket",
        "example_count": 4,
        "baseline": {
            "leave_one_out_majority_accuracy": 0.0,
            "leave_one_out_nearest_neighbor_accuracy": 0.25,
        },
        "neural": {
            "model_name": "sparse-softmax-model-sequence-nn",
            "backend": "python-standard-library",
            "leave_one_out_accuracy": 1.0,
            "DeltaH": 1.0,
        },
        "delta": {"accuracy_vs_nearest_neighbor": 0.75},
        "interpretation": "neural_better",
        "notes": ["sample note"],
    }


def test_model_sequence_comparison_report_dict() -> None:
    report = model_sequence_comparison_report_dict(comparison_result())

    assert report["report_type"] == "model_sequence_nn_comparison_report"
    assert report["baseline_accuracy"] == 0.25
    assert report["neural_accuracy"] == 1.0
    assert report["control_warning"] == "not_a_control_result"


def test_model_sequence_comparison_report_markdown() -> None:
    report = model_sequence_comparison_report_dict(comparison_result())
    markdown = model_sequence_comparison_report_markdown(report)

    assert "TraceLeak Model Sequence NN Comparison Report" in markdown
    assert "Nearest-neighbor baseline" in markdown
    assert "Sparse-softmax NN" in markdown
    assert "neural_better" in markdown


def test_count_pattern_sample_favors_count_learning_over_jaccard_presence() -> None:
    import json
    from pathlib import Path

    data = json.loads(
        Path("examples/synthetic/model_sequence_nn_count_pattern_sample.json").read_text(
            encoding="utf-8"
        )
    )
    result = compare_model_sequence_nn_to_baseline(data, epochs=80, learning_rate=0.8)

    assert result["baseline"]["leave_one_out_nearest_neighbor_accuracy"] < result["neural"][
        "leave_one_out_accuracy"
    ]
    assert result["interpretation"] == "neural_better"
