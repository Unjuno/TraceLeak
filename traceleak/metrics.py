"""Leakage metrics for TraceLeak."""

from __future__ import annotations

import math
from collections.abc import Sequence


class MetricError(ValueError):
    """Raised when a metric input is invalid."""


def delta_h(candidate_count: int, remaining_count: int) -> float:
    """Return candidate-space reduction in bits.

    DeltaH = log2(|C|) - log2(|C_k|)

    Args:
        candidate_count: Size of the original candidate set.
        remaining_count: Size of the remaining candidate set.

    Returns:
        Candidate-space reduction in bits.
    """

    if candidate_count <= 0:
        raise MetricError("candidate_count must be positive")
    if remaining_count <= 0:
        raise MetricError("remaining_count must be positive")
    if remaining_count > candidate_count:
        raise MetricError("remaining_count must not exceed candidate_count")
    return math.log2(candidate_count) - math.log2(remaining_count)


def top_k_recall(y_true: Sequence[object], y_topk: Sequence[Sequence[object]]) -> float:
    """Compute top-k recall for ranked candidate outputs."""

    if len(y_true) != len(y_topk):
        raise MetricError("y_true and y_topk must have the same length")
    if not y_true:
        raise MetricError("inputs must not be empty")

    hits = sum(1 for truth, candidates in zip(y_true, y_topk, strict=True) if truth in candidates)
    return hits / len(y_true)


def accuracy(y_true: Sequence[object], y_pred: Sequence[object]) -> float:
    """Compute exact-match accuracy."""

    if len(y_true) != len(y_pred):
        raise MetricError("y_true and y_pred must have the same length")
    if not y_true:
        raise MetricError("inputs must not be empty")

    hits = sum(1 for truth, pred in zip(y_true, y_pred, strict=True) if truth == pred)
    return hits / len(y_true)
