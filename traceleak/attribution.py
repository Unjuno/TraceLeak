"""Attribution primitives for source-level leakage localization.

The functions in this module are intentionally lightweight. They do not train
models. Instead, they provide reusable scoring utilities for local experiments
that have already produced per-feature or per-group measurements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class AttributionError(ValueError):
    """Raised when attribution inputs are invalid."""


@dataclass(frozen=True, order=True)
class AttributionScore:
    """Leakage contribution score for a source-level group."""

    contribution: float
    group_id: str
    group_type: str
    evidence: tuple[str, ...] = ()
    location: str | None = None
    metadata: dict[str, Any] | None = None


def ablation_drop(full_score: float, ablated_score: float) -> float:
    """Return the score lost after removing a feature group.

    For TraceLeak's DeltaH workflow this corresponds to:

        s_j = DeltaH(X) - DeltaH(X_without_j)

    Negative values are allowed by default because real measurements may be
    noisy. Callers can clamp later if they need a non-negative report field.
    """

    if full_score < 0:
        raise AttributionError("full_score must be non-negative")
    if ablated_score < 0:
        raise AttributionError("ablated_score must be non-negative")
    return full_score - ablated_score


def rank_attributions(scores: list[AttributionScore], *, descending: bool = True) -> list[AttributionScore]:
    """Rank attribution scores by contribution.

    Ties are resolved by group_id for deterministic output.
    """

    return sorted(scores, key=lambda score: (score.contribution, score.group_id), reverse=descending)


def make_ablation_scores(
    *,
    full_score: float,
    ablated_scores: dict[str, float],
    group_type: str,
    evidence: tuple[str, ...] = ("ablation",),
    locations: dict[str, str] | None = None,
) -> list[AttributionScore]:
    """Create ranked AttributionScore objects from ablation measurements."""

    if not ablated_scores:
        raise AttributionError("ablated_scores must not be empty")

    locations = locations or {}
    scores = [
        AttributionScore(
            contribution=ablation_drop(full_score, ablated),
            group_id=group_id,
            group_type=group_type,
            evidence=evidence,
            location=locations.get(group_id),
            metadata={"full_score": full_score, "ablated_score": ablated},
        )
        for group_id, ablated in ablated_scores.items()
    ]
    return rank_attributions(scores)
