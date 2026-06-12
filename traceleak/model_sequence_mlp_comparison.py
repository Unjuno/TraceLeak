"""Compare model-sequence MLP results against lightweight baselines."""

from __future__ import annotations

from typing import Any

from traceleak.model_sequence_baseline import evaluate_model_sequence_baselines
from traceleak.model_sequence_comparison import classify_nn_baseline_delta
from traceleak.model_sequence_mlp import train_model_sequence_mlp_result


class ModelSequenceMLPComparisonError(ValueError):
    """Raised when MLP comparison cannot be computed."""


def compare_model_sequence_mlp_to_baseline(
    data: dict[str, Any],
    *,
    epochs: int = 200,
    learning_rate: float = 0.2,
    l2: float = 0.0001,
    hidden_size: int = 8,
) -> dict[str, Any]:
    baseline = evaluate_model_sequence_baselines(data)
    neural = train_model_sequence_mlp_result(
        data,
        experiment_id="exp_model_sequence_mlp_comparison",
        epochs=epochs,
        learning_rate=learning_rate,
        l2=l2,
        hidden_size=hidden_size,
    )
    baseline_accuracy = float(baseline["baselines"]["leave_one_out_nearest_neighbor_accuracy"])
    neural_accuracy = float(neural["metrics"]["leave_one_out"]["accuracy"])
    delta_accuracy = neural_accuracy - baseline_accuracy
    return {
        "result_type": "model_sequence_nn_vs_baseline",
        "input_format": data.get("format", "unknown"),
        "target": neural["target"],
        "view": neural["view"],
        "label_name": neural.get("label_name", data.get("label_name", "label")),
        "example_count": neural["metrics"]["leave_one_out"]["example_count"],
        "label_distribution": neural.get("label_distribution", {}),
        "baseline": {
            "leave_one_out_majority_accuracy": baseline["baselines"][
                "leave_one_out_majority_accuracy"
            ],
            "leave_one_out_nearest_neighbor_accuracy": baseline_accuracy,
        },
        "neural": {
            "model_name": neural["model"]["name"],
            "backend": neural["model"].get("backend", "unknown"),
            "architecture": neural["model"].get("architecture", "one-hidden-layer-tanh-softmax"),
            "hidden_size": neural["model"].get("hidden_size"),
            "leave_one_out_accuracy": neural_accuracy,
            "DeltaH": neural["metrics"]["leave_one_out"]["DeltaH"],
            "top_attributions": list(neural.get("attributions", [])),
        },
        "delta": {"accuracy_vs_nearest_neighbor": delta_accuracy},
        "interpretation": classify_nn_baseline_delta(delta_accuracy),
        "notes": [
            "Comparison uses the same input and leave-one-out protocol for both evaluators.",
            "Neural evaluator architecture: one-hidden-layer-tanh-softmax.",
        ],
    }
