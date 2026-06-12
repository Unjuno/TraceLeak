import json
from pathlib import Path

from traceleak.model_sequence_comparison import (
    classify_nn_baseline_delta,
    compare_model_sequence_nn_to_baseline,
)


def load_sample(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_compare_model_sequence_nn_to_baseline_on_hard_sample() -> None:
    result = compare_model_sequence_nn_to_baseline(
        load_sample("examples/synthetic/model_sequence_nn_hard_sample.json"),
        epochs=80,
        learning_rate=0.8,
    )

    assert result["result_type"] == "model_sequence_nn_vs_baseline"
    assert result["example_count"] == 8
    assert result["neural"]["backend"] == "python-standard-library"
    assert 0.0 <= result["neural"]["leave_one_out_accuracy"] <= 1.0
    assert result["interpretation"] in {"neural_better", "baseline_better", "similar"}


def test_negative_control_does_not_claim_perfect_neural_signal() -> None:
    result = compare_model_sequence_nn_to_baseline(
        load_sample("examples/synthetic/model_sequence_nn_negative_control_sample.json"),
        epochs=80,
        learning_rate=0.8,
    )

    assert result["example_count"] == 8
    assert result["neural"]["leave_one_out_accuracy"] < 1.0
    assert result["neural"]["DeltaH"] < 1.0


def test_classify_nn_baseline_delta() -> None:
    assert classify_nn_baseline_delta(0.05) == "neural_better"
    assert classify_nn_baseline_delta(-0.05) == "baseline_better"
    assert classify_nn_baseline_delta(0.0) == "similar"
