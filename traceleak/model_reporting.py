"""Convert validated model result files into TraceLeak reports."""

from __future__ import annotations

from typing import Any

from traceleak.model_results import attributions_from_model_result, validate_model_result
from traceleak.reporting import attribution_report_dict


class ModelReportingError(ValueError):
    """Raised when a model result cannot be rendered as a report."""


def model_result_to_report(
    result: dict[str, Any],
    *,
    split: str = "test",
    metric: str = "DeltaH",
    public_safe: bool = True,
) -> dict[str, Any]:
    """Convert a model result dictionary into a TraceLeak attribution report."""

    validate_model_result(result, public_safe=public_safe)
    score = _select_score(result, split=split, metric=metric)
    attributions = attributions_from_model_result(result)
    model = result["model"]
    notes = list(result.get("notes", []))
    notes.append(f"model: {model.get('name')} ({model.get('type')})")
    notes.append(f"metric source: metrics.{split}.{metric}")

    return attribution_report_dict(
        target=result["target"],
        view=result["view"],
        metric=metric,
        score=score,
        attributions=attributions,
        notes=notes,
    )


def _select_score(result: dict[str, Any], *, split: str, metric: str) -> float:
    metrics = result.get("metrics", {})
    if split not in metrics:
        available = ", ".join(sorted(metrics))
        raise ModelReportingError(f"metric split not found: {split!r}; available: {available}")
    values = metrics[split]
    if metric not in values:
        available = ", ".join(sorted(values))
        raise ModelReportingError(f"metric not found in split {split!r}: {metric!r}; available: {available}")
    return float(values[metric])
