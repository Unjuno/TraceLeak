import json
from pathlib import Path

import pytest

from traceleak.model_results import validate_model_result
from traceleak.model_sequence_nn import (
    ModelSequenceNNError,
    chance_adjusted_delta_h_proxy,
    parse_model_sequence_nn_vectors,
    train_model_sequence_nn_result,
)


def sample_input() -> dict:
    return json.loads(
        Path("examples/synthetic/model_sequence_baseline_sample.json").read_text(encoding="utf-8")
    )


def test_parse_model_sequence_nn_vectors_from_count_records() -> None:
    vectors = parse_model_sequence_nn_vectors(sample_input())

    assert len(vectors) == 4
    assert vectors[0].label == "1"
    assert vectors[0].features["event_type=branch"] == 1.0


def test_train_model_sequence_nn_result_is_valid_public_model_result() -> None:
    result = train_model_sequence_nn_result(
        sample_input(),
        experiment_id="exp_test_model_sequence_nn",
        epochs=80,
        learning_rate=0.8,
    )

    validate_model_result(result)
    assert result["result_type"] == "model_sequence_nn"
    assert result["model"]["type"] == "neural"
    assert result["model"]["backend"] == "python-standard-library"
    assert result["metrics"]["leave_one_out"]["accuracy"] == 1.0
    assert result["metrics"]["leave_one_out"]["DeltaH"] == 1.0
    assert result["attributions"]


def test_chance_adjusted_delta_h_proxy_binary_cases() -> None:
    assert chance_adjusted_delta_h_proxy(0.5, 2) == 0.0
    assert chance_adjusted_delta_h_proxy(1.0, 2) == 1.0


def test_train_model_sequence_nn_rejects_single_example_per_label() -> None:
    data = sample_input()
    data["records"] = [data["records"][0], data["records"][2]]

    with pytest.raises(ModelSequenceNNError, match="at least two examples per label"):
        train_model_sequence_nn_result(data)
