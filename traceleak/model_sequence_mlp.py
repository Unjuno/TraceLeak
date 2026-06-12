"""Dependency-light MLP over model-sequence token counts."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any

from traceleak.baselines import LabeledFeatureVector, label_distribution
from traceleak.metrics import accuracy
from traceleak.model_sequence_nn import (
    ModelSequenceNNError,
    chance_adjusted_delta_h_proxy,
    parse_model_sequence_nn_vectors,
)


@dataclass(frozen=True)
class ModelSequenceMLP:
    labels: tuple[str, ...]
    vocabulary: tuple[str, ...]
    w_in: dict[str, list[float]]
    b_hidden: list[float]
    w_out: dict[str, list[float]]
    b_out: dict[str, float]
    hidden_size: int


def train_model_sequence_mlp_result(
    data: dict[str, Any],
    *,
    experiment_id: str = "exp_model_sequence_mlp_local",
    epochs: int = 200,
    learning_rate: float = 0.2,
    l2: float = 0.0001,
    hidden_size: int = 8,
    top_k_attributions: int = 8,
) -> dict[str, Any]:
    vectors = parse_model_sequence_nn_vectors(data)
    _require_loo(vectors)
    y_true = [item.label for item in vectors]
    y_pred = leave_one_out_mlp_predictions(
        vectors,
        epochs=epochs,
        learning_rate=learning_rate,
        l2=l2,
        hidden_size=hidden_size,
    )
    model = train_mlp(
        vectors,
        epochs=epochs,
        learning_rate=learning_rate,
        l2=l2,
        hidden_size=hidden_size,
    )
    loo_accuracy = accuracy(y_true, y_pred)
    label_count = len(model.labels)
    return {
        "experiment_id": experiment_id,
        "target": str(data.get("target") or _common_metadata(vectors, "target") or "unknown"),
        "view": str(data.get("view") or _common_metadata(vectors, "view") or "redacted"),
        "result_type": "model_sequence_nn",
        "input_format": data.get("format", "unknown"),
        "label_name": data.get("label_name", "label"),
        "feature_source": "model_sequence_token_counts",
        "model": {
            "name": "mlp-model-sequence-nn",
            "type": "neural",
            "backend": "python-standard-library",
            "architecture": "one-hidden-layer-tanh-softmax",
            "feature_normalization": "l1_count_normalization",
            "epochs": epochs,
            "learning_rate": learning_rate,
            "l2": l2,
            "hidden_size": hidden_size,
            "label_count": label_count,
            "feature_count": len(model.vocabulary),
        },
        "metrics": {
            "leave_one_out": {
                "accuracy": loo_accuracy,
                "top_1_recall": loo_accuracy,
                "DeltaH": chance_adjusted_delta_h_proxy(loo_accuracy, label_count),
                "example_count": len(vectors),
            }
        },
        "label_distribution": label_distribution(vectors),
        "attributions": mlp_attributions(model, top_k=top_k_attributions),
        "notes": [
            "This is a local one-hidden-layer MLP over model-sequence token counts.",
            "Backend: Python standard library; no PyTorch/TensorFlow dependency.",
            "This is a toy/local validation tier unless the input file is an actual collected trace-derived sample.",
        ],
    }


def train_mlp(
    examples: list[LabeledFeatureVector],
    *,
    epochs: int = 200,
    learning_rate: float = 0.2,
    l2: float = 0.0001,
    hidden_size: int = 8,
) -> ModelSequenceMLP:
    _require_basic(examples)
    _validate_params(epochs=epochs, learning_rate=learning_rate, l2=l2, hidden_size=hidden_size)
    labels = tuple(sorted({item.label for item in examples}))
    vocabulary = tuple(sorted(_vocabulary(examples)))
    w_in = {name: [_init(f"i:{name}", j) for j in range(hidden_size)] for name in vocabulary}
    b_hidden = [0.0 for _ in range(hidden_size)]
    w_out = {label: [_init(f"o:{label}", j) for j in range(hidden_size)] for label in labels}
    b_out = {label: 0.0 for label in labels}
    rows = [(item.label, _normalize(item.features)) for item in examples]
    for _ in range(epochs):
        for true_label, features in rows:
            hidden, probs = _forward(labels, w_in, b_hidden, w_out, b_out, features)
            out_err = {label: probs[label] - (1.0 if label == true_label else 0.0) for label in labels}
            old_out = {label: list(w_out[label]) for label in labels}
            for label in labels:
                for j, h_value in enumerate(hidden):
                    w_out[label][j] -= learning_rate * (out_err[label] * h_value + l2 * w_out[label][j])
                b_out[label] -= learning_rate * out_err[label]
            h_err = []
            for j, h_value in enumerate(hidden):
                downstream = sum(out_err[label] * old_out[label][j] for label in labels)
                h_err.append((1.0 - h_value * h_value) * downstream)
            for name, value in features.items():
                for j, error in enumerate(h_err):
                    w_in[name][j] -= learning_rate * (error * value + l2 * w_in[name][j])
            for j, error in enumerate(h_err):
                b_hidden[j] -= learning_rate * error
    return ModelSequenceMLP(labels, vocabulary, w_in, b_hidden, w_out, b_out, hidden_size)


def leave_one_out_mlp_predictions(
    examples: list[LabeledFeatureVector],
    *,
    epochs: int = 200,
    learning_rate: float = 0.2,
    l2: float = 0.0001,
    hidden_size: int = 8,
) -> list[str]:
    _require_loo(examples)
    predictions = []
    for index, example in enumerate(examples):
        train = [item for offset, item in enumerate(examples) if offset != index]
        model = train_mlp(train, epochs=epochs, learning_rate=learning_rate, l2=l2, hidden_size=hidden_size)
        predictions.append(predict_mlp_label(model, example.features))
    return predictions


def predict_mlp_label(model: ModelSequenceMLP, features: dict[str, float]) -> str:
    _, probs = _forward(model.labels, model.w_in, model.b_hidden, model.w_out, model.b_out, _normalize(features))
    return max(model.labels, key=lambda label: probs[label])


def mlp_attributions(model: ModelSequenceMLP, *, top_k: int = 8) -> list[dict[str, Any]]:
    rows = []
    for name in model.vocabulary:
        score = 0.0
        for j, in_weight in enumerate(model.w_in[name]):
            outs = [model.w_out[label][j] for label in model.labels]
            score += abs(in_weight) * abs(max(outs) - min(outs))
        if score > 0.0:
            rows.append({"group_id": name, "group_type": "model_sequence_token", "score": round(score, 12), "evidence": ["mlp_input_hidden_output_bridge"]})
    rows.sort(key=lambda item: (-float(item["score"]), str(item["group_id"])))
    return rows[:top_k]


def _forward(labels, w_in, b_hidden, w_out, b_out, features):
    hidden = []
    for j, bias in enumerate(b_hidden):
        activation = bias + sum(w_in.get(name, [0.0] * len(b_hidden))[j] * value for name, value in features.items())
        hidden.append(math.tanh(activation))
    scores = {label: b_out[label] + sum(w_out[label][j] * hidden[j] for j in range(len(hidden))) for label in labels}
    peak = max(scores.values())
    exp_scores = {label: math.exp(score - peak) for label, score in scores.items()}
    total = sum(exp_scores.values())
    return hidden, {label: value / total for label, value in exp_scores.items()}


def _normalize(features: dict[str, float]) -> dict[str, float]:
    scale = sum(abs(value) for value in features.values() if value != 0.0)
    if scale <= 0.0:
        raise ModelSequenceNNError("feature vector must contain at least one non-zero value")
    return {name: value / scale for name, value in features.items() if value != 0.0}


def _vocabulary(examples: list[LabeledFeatureVector]) -> set[str]:
    return {name for item in examples for name, value in item.features.items() if value != 0.0}


def _init(name: str, index: int) -> float:
    seed = sum((offset + 1) * ord(char) for offset, char in enumerate(f"{name}:{index}"))
    return (((seed % 2001) / 1000.0) - 1.0) * 0.05


def _validate_params(*, epochs: int, learning_rate: float, l2: float, hidden_size: int) -> None:
    if not isinstance(epochs, int) or epochs <= 0:
        raise ModelSequenceNNError("epochs must be a positive integer")
    if not math.isfinite(learning_rate) or learning_rate <= 0.0:
        raise ModelSequenceNNError("learning_rate must be a positive finite number")
    if not math.isfinite(l2) or l2 < 0.0:
        raise ModelSequenceNNError("l2 must be a non-negative finite number")
    if not isinstance(hidden_size, int) or hidden_size <= 0:
        raise ModelSequenceNNError("hidden_size must be a positive integer")


def _require_basic(examples: list[LabeledFeatureVector]) -> None:
    if len(examples) < 2:
        raise ModelSequenceNNError("at least two examples are required")
    if len({item.label for item in examples}) < 2:
        raise ModelSequenceNNError("at least two labels are required")


def _require_loo(examples: list[LabeledFeatureVector]) -> None:
    _require_basic(examples)
    counts = Counter(item.label for item in examples)
    rare = sorted(label for label, count in counts.items() if count < 2)
    if rare:
        raise ModelSequenceNNError("leave-one-out MLP evaluation requires at least two examples per label; too few examples for: " + ", ".join(rare))


def _common_metadata(examples: list[LabeledFeatureVector], key: str) -> str | None:
    values = sorted({str(item.metadata.get(key)) for item in examples if item.metadata and item.metadata.get(key) is not None})
    if len(values) == 1:
        return values[0]
    return None
