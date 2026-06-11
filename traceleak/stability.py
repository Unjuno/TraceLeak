"""Repeated-run stability checks for TraceLeak patch verification.

This module summarizes repeated before/after measurements. It intentionally uses
only the Python standard library so it remains part of the lightweight workflow.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from traceleak.patch_verification import classify_delta
from traceleak.schema import PUBLIC_SAFE_VIEWS, SECRET_EQUIVALENT_KEYS


class StabilityError(ValueError):
    """Raised when a stability input is invalid."""


def load_stability_input(path: str | Path) -> dict[str, Any]:
    """Load a repeated-run stability JSON file."""

    input_path = Path(path)
    if not input_path.exists():
        raise StabilityError(f"stability input file not found: {input_path}")
    try:
        return json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StabilityError(f"invalid JSON in {input_path}: {exc}") from exc


def validate_stability_input(data: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate a repeated-run stability input dictionary."""

    for key in ("stability_id", "target", "view", "metric", "before_scores", "after_scores"):
        if key not in data:
            raise StabilityError(f"missing required stability field: {key}")

    _require_non_empty_string(data["stability_id"], "stability_id")
    _require_non_empty_string(data["target"], "target")
    _require_non_empty_string(data["metric"], "metric")

    view = data["view"]
    _require_non_empty_string(view, "view")
    if public_safe and view not in PUBLIC_SAFE_VIEWS:
        raise StabilityError(f"view {view!r} is not allowed in public-safe stability input")

    _validate_score_list(data["before_scores"], "before_scores")
    _validate_score_list(data["after_scores"], "after_scores")
    _reject_secret_equivalent_fields(data)


def stability_summary(
    before_scores: list[float],
    after_scores: list[float],
    *,
    tolerance: float = 1e-9,
    min_margin: float = 1.0,
) -> dict[str, Any]:
    """Summarize repeated before/after scores.

    `margin` is the absolute mean delta divided by pooled standard deviation. If
    the pooled standard deviation is zero, the margin is infinite for non-zero
    deltas and zero for zero deltas.
    """

    _validate_score_list(before_scores, "before_scores")
    _validate_score_list(after_scores, "after_scores")
    _require_number(tolerance, "tolerance")
    _require_number(min_margin, "min_margin")
    if tolerance < 0:
        raise StabilityError("tolerance must be non-negative")
    if min_margin < 0:
        raise StabilityError("min_margin must be non-negative")

    before_mean = mean(before_scores)
    after_mean = mean(after_scores)
    before_stdev = sample_stdev(before_scores)
    after_stdev = sample_stdev(after_scores)
    mean_delta = before_mean - after_mean
    direction = classify_delta(mean_delta, tolerance=tolerance)
    pooled = pooled_stdev(before_scores, after_scores)
    margin = _stability_margin(mean_delta, pooled)
    status = direction if direction == "unchanged" or margin >= min_margin else "inconclusive"

    return {
        "before_count": len(before_scores),
        "after_count": len(after_scores),
        "before_mean": before_mean,
        "after_mean": after_mean,
        "before_stdev": before_stdev,
        "after_stdev": after_stdev,
        "pooled_stdev": pooled,
        "mean_delta": mean_delta,
        "relative_delta": _relative_delta(mean_delta, before_mean),
        "margin": margin,
        "direction": direction,
        "status": status,
    }


def stability_result(data: dict[str, Any], *, public_safe: bool = True) -> dict[str, Any]:
    """Validate input and return a normalized stability result."""

    validate_stability_input(data, public_safe=public_safe)
    summary = stability_summary(data["before_scores"], data["after_scores"])
    return {
        "result_type": "repeated_run_stability",
        "stability_id": data["stability_id"],
        "target": data["target"],
        "view": data["view"],
        "metric": data["metric"],
        "summary": summary,
        "notes": data.get("notes", []),
    }


def mean(values: list[float]) -> float:
    """Return arithmetic mean."""

    _validate_score_list(values, "values")
    return float(sum(values) / len(values))


def sample_variance(values: list[float]) -> float:
    """Return sample variance, or zero for one value."""

    _validate_score_list(values, "values")
    if len(values) == 1:
        return 0.0
    center = mean(values)
    return float(sum((value - center) ** 2 for value in values) / (len(values) - 1))


def sample_stdev(values: list[float]) -> float:
    """Return sample standard deviation."""

    return math.sqrt(sample_variance(values))


def pooled_stdev(left: list[float], right: list[float]) -> float:
    """Return pooled sample standard deviation for two score lists."""

    _validate_score_list(left, "left")
    _validate_score_list(right, "right")
    degrees = len(left) + len(right) - 2
    if degrees <= 0:
        return 0.0
    numerator = (len(left) - 1) * sample_variance(left) + (len(right) - 1) * sample_variance(right)
    return math.sqrt(numerator / degrees)


def _stability_margin(delta: float, pooled: float) -> float:
    if pooled == 0:
        return math.inf if delta != 0 else 0.0
    return abs(delta) / pooled


def _relative_delta(delta: float, before_mean: float) -> float | None:
    if before_mean == 0:
        return None
    return delta / before_mean


def _validate_score_list(values: Any, name: str) -> None:
    if not isinstance(values, list) or not values:
        raise StabilityError(f"{name} must be a non-empty list")
    for index, value in enumerate(values):
        _require_number(value, f"{name}[{index}]")


def _require_non_empty_string(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise StabilityError(f"{name} must be a non-empty string")


def _require_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool) or not math.isfinite(value):
        raise StabilityError(f"{name} must be a finite number")


def _reject_secret_equivalent_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in SECRET_EQUIVALENT_KEYS:
                raise StabilityError(f"secret-equivalent field is not allowed: {key}")
            _reject_secret_equivalent_fields(child)
    elif isinstance(value, list):
        for child in value:
            _reject_secret_equivalent_fields(child)
