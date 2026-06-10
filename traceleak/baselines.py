"""Lightweight baseline evaluators for TraceLeak.

These helpers are designed for sanity checks before local NN training. They do
not depend on scikit-learn, NumPy, PyTorch, or TensorFlow.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from traceleak.metrics import accuracy


class BaselineError(ValueError):
    """Raised when baseline inputs are invalid."""


@dataclass(frozen=True)
class LabeledFeatureVector:
    """A sparse feature vector with one lab-only evaluation label."""

    label: str
    features: dict[str, float]
    run_id: str | None = None
    metadata: dict[str, Any] | None = None


def majority_label(labels: list[str]) -> str:
    """Return the most common label with deterministic tie-breaking."""

    if not labels:
        raise BaselineError("labels must not be empty")
    counts = Counter(labels)
    max_count = max(counts.values())
    tied = sorted(label for label, count in counts.items() if count == max_count)
    return tied[0]


def majority_predictions(train_labels: list[str], count: int) -> list[str]:
    """Predict the training-set majority label for count examples."""

    if count < 0:
        raise BaselineError("count must be non-negative")
    return [majority_label(train_labels)] * count


def leave_one_out_majority_accuracy(examples: list[LabeledFeatureVector]) -> float:
    """Evaluate a majority-label baseline with leave-one-out splits."""

    _require_two_examples(examples)
    y_true: list[str] = []
    y_pred: list[str] = []
    for index, example in enumerate(examples):
        train_labels = [item.label for offset, item in enumerate(examples) if offset != index]
        y_true.append(example.label)
        y_pred.append(majority_label(train_labels))
    return accuracy(y_true, y_pred)


def leave_one_out_nearest_neighbor_accuracy(examples: list[LabeledFeatureVector]) -> float:
    """Evaluate a sparse Jaccard nearest-neighbor baseline with leave-one-out splits."""

    _require_two_examples(examples)
    y_true: list[str] = []
    y_pred: list[str] = []
    for index, example in enumerate(examples):
        train = [item for offset, item in enumerate(examples) if offset != index]
        y_true.append(example.label)
        y_pred.append(nearest_neighbor_predict_one(train, example))
    return accuracy(y_true, y_pred)


def nearest_neighbor_predict_one(train: list[LabeledFeatureVector], query: LabeledFeatureVector) -> str:
    """Predict one label using sparse Jaccard similarity over non-zero features."""

    if not train:
        raise BaselineError("train must not be empty")

    query_set = nonzero_feature_set(query.features)
    best_label: str | None = None
    best_score = -1.0
    for candidate in train:
        score = jaccard_similarity(query_set, nonzero_feature_set(candidate.features))
        if score > best_score:
            best_score = score
            best_label = candidate.label
    if best_label is None:  # pragma: no cover - defensive only.
        raise BaselineError("could not produce nearest-neighbor prediction")
    return best_label


def nonzero_feature_set(features: dict[str, float]) -> set[str]:
    """Return names of non-zero features."""

    return {name for name, value in features.items() if value != 0.0}


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    """Return Jaccard similarity for two feature-name sets."""

    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def label_distribution(examples: list[LabeledFeatureVector]) -> dict[str, int]:
    """Return label counts."""

    if not examples:
        raise BaselineError("examples must not be empty")
    return dict(sorted(Counter(item.label for item in examples).items()))


def _require_two_examples(examples: list[LabeledFeatureVector]) -> None:
    if len(examples) < 2:
        raise BaselineError("at least two labeled examples are required")
