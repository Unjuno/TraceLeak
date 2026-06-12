import json
from pathlib import Path

from traceleak.model_sequence_comparison import compare_model_sequence_nn_to_baseline


CONTROL_PATHS = [
    "examples/synthetic/model_sequence_nn_control_seed_001.json",
    "examples/synthetic/model_sequence_nn_control_seed_002.json",
    "examples/synthetic/model_sequence_nn_control_seed_003.json",
]


def test_multiple_controls_do_not_create_high_neural_accuracy() -> None:
    accuracies = []
    for path in CONTROL_PATHS:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        result = compare_model_sequence_nn_to_baseline(data, epochs=80, learning_rate=0.8)
        accuracies.append(result["neural"]["leave_one_out_accuracy"])

    assert max(accuracies) <= 0.25
    assert sum(accuracies) / len(accuracies) <= 0.25
