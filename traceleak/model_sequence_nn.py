"""Minimal local neural training over model sequence token counts.

This module intentionally depends only on the Python standard library.  The
classifier is a deterministic single-layer softmax network over sparse
variable/control-flow token counts.  It is a small local training path, not a
large PyTorch/TensorFlow experiment.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any

from traceleak.baselines import LabeledFeatureVector, label_distribution
from traceleak.metrics import accuracy
from traceleak.model_sequence_baseline import (
    ModelSequenceBaselineError,
    labeled_counts_to_feature_vector,
    labeled_sequence_to_feature_vector,
    parse_labeled_model_sequence_counts,
    parse_labeled_model_sequences,
)


class ModelSequenceNNError(ValueError):
    """Raised when model sequence neural training cannot be completed."""


@dataclass(frozen=True)
class SparseSoftmaxModel:
    """A trained sparse single-layer softmax classifier."""

    labels: tuple[str, ...]
    vocabulary: tuple[str, ...]
    weights: dict[str, dict[str, float]]
    biases: dict[str, float]
    feature_normalization: str = "l1_count_normalization"


def parse_model_sequence_nn_vectors(data: dict[str, Any]) -> list[LabeledFeatureVector]:
    """Parse model sequence input into sparse labeled feature vectors."""

    try:
        if "records" in data:
            return [
                labeled_counts_to_feature_vector(example)
                for example in parse_labeled_model_sequence_counts(data)
            ]
        return [
            labeled_sequence_to_feature_vector(example)
            for example in parse_labeled_model_sequences(data)
        ]
    except ModelSequenceBaselineError as exc:
        raise ModelSequenceNNError(str(exc)) from exc


def train_model_sequence_nn_result(
    data: dict[str, Any],
    *,
    experiment_id: str = "exp_model_sequence_nn_local",
    epochs: int = 200,
    learning_rate: float = 0.8,
    l2: float = 0.0001,
    top_k_attributions: int = 8,
) -> dict[str, Any]:
    """Train a sparse softmax model and return a public-safe model result."""

    vectors = parse_model_sequence_nn_vectors(data)
    _require_leave_one_out_examples(vectors)

    predictions = leave_one_out_sparse_softmax_predictions(
        vectors,
        epochs=epochs,
        learning_rate=learning_rate,
        l2=l2,
    )
    y_true = [example.label for example in vectors]
    loo_accuracy = accuracy(y_true, predictions)

    model = train_sparse_softmax(
        vectors,
        epochs=epochs,
        learning_rate=learning_rate,
        l2=l2,
    )
    label_count = len(model.labels)
    delta_h_proxy = chance_adjusted_delta_h_proxy(loo_accuracy, label_count)

    return {
        "experiment_id": experiment_id,
        "target": _target_name(data, vectors),
        "view": _view_name(data, vectors),
        "result_type": "model_sequence_nn",
        "input_format": data.get("format", "unknown"),
        "label_name": data.get("label_name", "label"),
        "feature_source": "model_sequence_token_counts",
        "model": {
            "name": "sparse-softmax-model-sequence-nn",
            "type": "neural",
            "backend": "python-standard-library",
            "architecture": "single-layer-softmax",
            "feature_normalization": model.feature_normalization,
            "epochs": epochs,
            "learning_rate": learning_rate,
            "l2": l2,
            "label_count": label_count,
            "feature_count": len(model.vocabulary),
        },
        "metrics": {
            "leave_one_out": {
                "accuracy": loo_accuracy,
                "top_1_recall": loo_accuracy,
                "DeltaH": delta_h_proxy,
                "example_count": len(vectors),
            }
        },
        "label_distribution": label_distribution(vectors),
        "attributions": sparse_softmax_attributions(model, top_k=top_k_attributions),
        "notes": _result_notes(len(vectors)),
    }


def train_sparse_softmax(
    examples: list[LabeledFeatureVector],
    *,
    epochs: int = 200,
    learning_rate: float = 0.8,
    l2: float = 0.0001,
) -> SparseSoftmaxModel:
    """Train a deterministic sparse softmax classifier."""

    _require_basic_training_examples(examples)
    _validate_hyperparameters(epochs=epochs, learning_rate=learning_rate, l2=l2)

    labels = tuple(sorted({example.label for example in examples}))
    vocabulary = tuple(sorted(_feature_vocabulary(examples)))
    weights: dict[str, dict[str, float]] = {label: {} for label in labels}
    biases = {label: 0.0 for label in labels}
    normalized_examples = [
        (example.label, _l1_normalize_features(example.features)) for example in examples
    ]

    for _ in range(epochs):
        for true_label, features in normalized_examples:
            probabilities = _predict_probabilities(labels, weights, biases, features)
            for label in labels:
                error = probabilities[label] - (1.0 if label == true_label else 0.0)
                _apply_sparse_gradient(
                    weights[label],
                    features,
                    error=error,
                    learning_rate=learning_rate,
                    l2=l2,
                )
                biases[label] -= learning_rate * error

    return SparseSoftmaxModel(
        labels=labels,
        vocabulary=vocabulary,
        weights=weights,
        biases=biases,
    )


def leave_one_out_sparse_softmax_predictions(
    examples: list[LabeledFeatureVector],
    *,
    epochs: int = 200,
    learning_rate: float = 0.8,
    l2: float = 0.0001,
) -> list[str]:
    """Return leave-one-out predictions from freshly trained sparse models."""

    _require_leave_one_out_examples(examples)
    predictions = []
    for index, example in enumerate(examples):
        train = [item for offset, item in enumerate(examples) if offset != index]
        model = train_sparse_softmax(
            train,
            epochs=epochs,
            learning_rate=learning_rate,
            l2=l2,
        )
        predictions.append(predict_sparse_softmax_label(model, example.features))
    return predictions


def predict_sparse_softmax_label(model: SparseSoftmaxModel, features: dict[str, float]) -> str:
    """Predict the most likely label for one sparse feature vector."""

    normalized = _l1_normalize_features(features)
    probabilities = _predict_probabilities(model.labels, model.weights, model.biases, normalized)
    return max(model.labels, key=lambda label: probabilities[label])


def sparse_softmax_attributions(model: SparseSoftmaxModel, *, top_k: int = 8) -> list[dict[str, Any]]:
    """Rank token features by cross-label weight separation."""

    if top_k < 0:
        raise ModelSequenceNNError("top_k must be non-negative")

    rows = []
    for feature in model.vocabulary:
        label_weights = [model.weights[label].get(feature, 0.0) for label in model.labels]
        score = max(label_weights) - min(label_weights)
        if score <= 0.0:
            continue
        rows.append(
            {
                "group_id": feature,
                "group_type": "model_sequence_token",
                "score": round(score, 12),
                "evidence": ["sparse_softmax_weight_separation"],
            }
        )
    rows.sort(key=lambda item: (-float(item["score"]), str(item["group_id"])))
    return rows[:top_k]


def chance_adjusted_delta_h_proxy(accuracy_value: float, label_count: int) -> float:
    """Return a chance-adjusted classification proxy in bits."""

    if label_count < 2:
        raise ModelSequenceNNError("label_count must be at least two")
    if not math.isfinite(accuracy_value) or accuracy_value < 0.0 or accuracy_value > 1.0:
        raise ModelSequenceNNError("accuracy_value must be a finite probability")

    chance_accuracy = 1.0 / label_count
    adjusted = max(0.0, (accuracy_value - chance_accuracy) / (1.0 - chance_accuracy))
    return adjusted * math.log2(label_count)


def _apply_sparse_gradient(
    weights: dict[str, float],
    features: dict[str, float],
    *,
    error: float,
    learning_rate: float,
    l2: float,
) -> None:
    for name, value in features.items():
        old_weight = weights.get(name, 0.0)
        gradient = error * value + l2 * old_weight
        new_weight = old_weight - learning_rate * gradient
        if abs(new_weight) < 1e-15:
            weights.pop(name, None)
        else:
            weights[name] = new_weight


def _predict_probabilities(
    labels: tuple[str, ...],
    weights: dict[str, dict[str, float]],
    biases: dict[str, float],
    features: dict[str, float],
) -> dict[str, float]:
    scores = {
        label: biases[label]
        + sum(weights[label].get(feature, 0.0) * value for feature, value in features.items())
        for label in labels
    }
    peak = max(scores.values())
    exp_scores = {label: math.exp(score - peak) for label, score in scores.items()}
    total = sum(exp_scores.values())
    return {label: value / total for label, value in exp_scores.items()}


def _l1_normalize_features(features: dict[str, float]) -> dict[str, float]:
    scale = sum(abs(value) for value in features.values() if value != 0.0)
    if scale <= 0.0:
        raise ModelSequenceNNError("feature vector must contain at least one non-zero value")
    return {name: value / scale for name, value in features.items() if value != 0.0}


def _feature_vocabulary(examples: list[LabeledFeatureVector]) -> set[str]:
    return {
        feature
        for example in examples
        for feature, value in example.features.items()
        if value != 0.0
    }


def _validate_hyperparameters(*, epochs: int, learning_rate: float, l2: float) -> None:
    if not isinstance(epochs, int) or epochs <= 0:
        raise ModelSequenceNNError("epochs must be a positive integer")
    if not math.isfinite(learning_rate) or learning_rate <= 0.0:
        raise ModelSequenceNNError("learning_rate must be a positive finite number")
    if not math.isfinite(l2) or l2 < 0.0:
        raise ModelSequenceNNError("l2 must be a non-negative finite number")


def _require_basic_training_examples(examples: list[LabeledFeatureVector]) -> None:
    if len(examples) < 2:
        raise ModelSequenceNNError("at least two examples are required")
    if len({example.label for example in examples}) < 2:
        raise ModelSequenceNNError("at least two labels are required")


def _require_leave_one_out_examples(examples: list[LabeledFeatureVector]) -> None:
    _require_basic_training_examples(examples)
    counts = Counter(example.label for example in examples)
    rare_labels = sorted(label for label, count in counts.items() if count < 2)
    if rare_labels:
        joined = ", ".join(rare_labels)
        raise ModelSequenceNNError(
            "leave-one-out neural evaluation requires at least two examples per label; "
            f"too few examples for: {joined}"
        )


def _target_name(data: dict[str, Any], examples: list[LabeledFeatureVector]) -> str:
    return str(data.get("target") or _common_metadata_value(examples, "target") or "unknown")


def _view_name(data: dict[str, Any], examples: list[LabeledFeatureVector]) -> str:
    return str(data.get("view") or _common_metadata_value(examples, "view") or "redacted")


def _common_metadata_value(examples: list[LabeledFeatureVector], key: str) -> str | None:
    values = sorted(
        {
            str(example.metadata.get(key))
            for example in examples
            if example.metadata and example.metadata.get(key) is not None
        }
    )
    if len(values) == 1:
        return values[0]
    return None


def _result_notes(example_count: int) -> list[str]:
    notes = [
        "This is a neural training result over model sequence token counts, not a placeholder import.",
        "Backend: Python standard library; no PyTorch/TensorFlow dependency.",
        "DeltaH is a chance-adjusted classification proxy, not an information-theoretic leakage proof.",
    ]
    if example_count < 16:
        notes.append("Small sample warning: use this as a pipeline check, not a performance claim.")
    return notes
