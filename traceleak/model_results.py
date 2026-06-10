"""Validation helpers for local model result files.

Model result files are the bridge between local modeling and TraceLeak's public-safe
reporting workflow. They should contain metrics and source-level attribution data,
not raw traces or local-only values.
"""

from __future__ import annotations

import json
from math import isfinite
from pathlib import Path
from typing import Any

from traceleak.attribution import AttributionScore, rank_attributions
from traceleak.schema import PUBLIC_SAFE_VIEWS, SECRET_EQUIVALENT_KEYS

ALLOWED_MODEL_TYPES: set[str] = {"baseline", "linear", "tree", "neural", "statistical", "other"}
ALLOWED_SPLITS: set[str] = {"train", "validation", "test", "holdout", "leave_one_out"}


class ModelResultError(ValueError):
    """Raised when a model result file is invalid."""


def load_model_result(path: str | Path) -> dict[str, Any]:
    """Load a JSON model result file."""

    model_path = Path(path)
    if not model_path.exists():
        raise ModelResultError(f"model result file not found: {model_path}")
    try:
        return json.loads(model_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelResultError(f"invalid JSON in {model_path}: {exc}") from exc


def validate_model_result(result: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate a model result dictionary."""

    for key in ("experiment_id", "target", "view", "model", "metrics"):
        if key not in result:
            raise ModelResultError(f"missing required model result field: {key}")

    _require_non_empty_string(result["experiment_id"], "experiment_id")
    _require_non_empty_string(result["target"], "target")

    view = result["view"]
    _require_non_empty_string(view, "view")
    if public_safe and view not in PUBLIC_SAFE_VIEWS:
        raise ModelResultError(f"view {view!r} is not allowed in public-safe model results")

    _validate_model(result["model"])
    _validate_metrics(result["metrics"])
    _validate_attributions(result.get("attributions", []))
    _reject_secret_equivalent_fields(result)


def model_result_summary(result: dict[str, Any]) -> dict[str, Any]:
    """Return a compact summary for validated model results."""

    return {
        "experiment_id": result["experiment_id"],
        "target": result["target"],
        "view": result["view"],
        "model_type": result["model"].get("type", "unknown"),
        "metric_count": len(result.get("metrics", {})),
        "attribution_count": len(result.get("attributions", [])),
    }


def attributions_from_model_result(result: dict[str, Any]) -> list[AttributionScore]:
    """Convert model result attribution rows to AttributionScore objects."""

    rows = []
    for item in result.get("attributions", []):
        rows.append(
            AttributionScore(
                contribution=float(item["score"]),
                group_id=item["group_id"],
                group_type=item.get("group_type", "unknown"),
                evidence=tuple(item.get("evidence", [])),
                location=item.get("location"),
                metadata=item.get("metadata"),
            )
        )
    return rank_attributions(rows)


def _validate_model(model: Any) -> None:
    if not isinstance(model, dict):
        raise ModelResultError("model must be an object")
    _require_non_empty_string(model.get("name"), "model.name")
    model_type = model.get("type")
    if model_type not in ALLOWED_MODEL_TYPES:
        allowed = ", ".join(sorted(ALLOWED_MODEL_TYPES))
        raise ModelResultError(f"invalid model.type: {model_type!r}; allowed: {allowed}")


def _validate_metrics(metrics: Any) -> None:
    if not isinstance(metrics, dict) or not metrics:
        raise ModelResultError("metrics must be a non-empty object")
    for split, values in metrics.items():
        if split not in ALLOWED_SPLITS:
            allowed = ", ".join(sorted(ALLOWED_SPLITS))
            raise ModelResultError(f"invalid metric split: {split!r}; allowed: {allowed}")
        if not isinstance(values, dict) or not values:
            raise ModelResultError(f"metrics.{split} must be a non-empty object")
        for name, value in values.items():
            _require_non_empty_string(name, f"metrics.{split} key")
            _require_number(value, f"metrics.{split}.{name}")


def _validate_attributions(attributions: Any) -> None:
    if attributions is None:
        return
    if not isinstance(attributions, list):
        raise ModelResultError("attributions must be a list when present")
    for index, item in enumerate(attributions):
        if not isinstance(item, dict):
            raise ModelResultError(f"attributions[{index}] must be an object")
        _require_non_empty_string(item.get("group_id"), f"attributions[{index}].group_id")
        _require_number(item.get("score"), f"attributions[{index}].score")
        if "group_type" in item:
            _require_non_empty_string(item["group_type"], f"attributions[{index}].group_type")
        if "evidence" in item and not isinstance(item["evidence"], list):
            raise ModelResultError(f"attributions[{index}].evidence must be a list")


def _require_non_empty_string(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ModelResultError(f"{name} must be a non-empty string")


def _require_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool) or not isfinite(value):
        raise ModelResultError(f"{name} must be a finite number")


def _reject_secret_equivalent_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in SECRET_EQUIVALENT_KEYS:
                raise ModelResultError(f"secret-equivalent field is not allowed: {key}")
            _reject_secret_equivalent_fields(child)
    elif isinstance(value, list):
        for child in value:
            _reject_secret_equivalent_fields(child)
