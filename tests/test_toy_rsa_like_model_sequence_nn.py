# ruff: noqa: I001

import json
from pathlib import Path

from traceleak.model_sequence_comparison import compare_model_sequence_nn_to_baseline


TOY_RATIO_TOKENS = {
    "event_token=loop:candidate_filter:toy_rsa_like_keygen:witness_refine_round",
    "event_token=loop:candidate_filter:toy_rsa_like_keygen:acceptance_confirm_round",
}

TOY_CONTROL_PATHS = [
    "examples/toy_rsa_like/model_sequence_nn_control_seed_001.json",
    "examples/toy_rsa_like/model_sequence_nn_control_seed_002.json",
    "examples/toy_rsa_like/model_sequence_nn_control_seed_003.json",
]


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_toy_rsa_like_count_pattern_sample_favors_count_learning() -> None:
    result = compare_model_sequence_nn_to_baseline(
        load_json("examples/toy_rsa_like/model_sequence_nn_count_pattern_sample.json"),
        epochs=80,
        learning_rate=0.8,
    )

    attribution_tokens = {item["group_id"] for item in result["neural"]["top_attributions"]}
    assert result["example_count"] == 16
    assert result["target"] == "toy-rsa-like-count-pattern"
    assert result["baseline"]["leave_one_out_nearest_neighbor_accuracy"] < result["neural"][
        "leave_one_out_accuracy"
    ]
    assert result["interpretation"] == "neural_better"
    assert attribution_tokens >= TOY_RATIO_TOKENS


def test_toy_rsa_like_controls_do_not_create_high_neural_accuracy() -> None:
    accuracies = []
    for path in TOY_CONTROL_PATHS:
        result = compare_model_sequence_nn_to_baseline(load_json(path), epochs=80, learning_rate=0.8)
        accuracies.append(result["neural"]["leave_one_out_accuracy"])

    assert max(accuracies) <= 0.25
    assert sum(accuracies) / len(accuracies) <= 0.25
