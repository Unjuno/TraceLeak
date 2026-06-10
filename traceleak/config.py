"""Experiment configuration validation for TraceLeak.

The config layer records what was evaluated: target, view, metric, inputs,
outputs, and safety expectations. It intentionally uses JSON-compatible
structures and avoids external dependencies.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from traceleak.schema import ALLOWED_VIEWS, PUBLIC_SAFE_VIEWS

MetricName = Literal["DeltaH", "accuracy", "top_k_recall", "mutual_information"]

ALLOWED_METRICS: set[str] = {"DeltaH", "accuracy", "top_k_recall", "mutual_information"}
ALLOWED_EXPERIMENT_TYPES: set[str] = {
    "synthetic",
    "toy-rsa",
    "openssl-rsa-keygen",
    "baseline",
    "reporting",
}


class ConfigError(ValueError):
    """Raised when an experiment config is invalid."""


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON experiment config."""

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"config file not found: {config_path}")
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {config_path}: {exc}") from exc


def validate_config(config: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate a TraceLeak experiment config.

    Args:
        config: Parsed experiment config.
        public_safe: If true, reject raw and cheat views.
    """

    required = ["experiment_id", "experiment_type", "target", "view", "metric", "inputs"]
    for key in required:
        if key not in config:
            raise ConfigError(f"missing required config field: {key}")

    experiment_id = config["experiment_id"]
    if not isinstance(experiment_id, str) or not experiment_id:
        raise ConfigError("experiment_id must be a non-empty string")

    experiment_type = config["experiment_type"]
    if experiment_type not in ALLOWED_EXPERIMENT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_EXPERIMENT_TYPES))
        raise ConfigError(f"invalid experiment_type: {experiment_type!r}; allowed: {allowed}")

    view = config["view"]
    if view not in ALLOWED_VIEWS:
        allowed = ", ".join(sorted(ALLOWED_VIEWS))
        raise ConfigError(f"invalid view: {view!r}; allowed: {allowed}")
    if public_safe and view not in PUBLIC_SAFE_VIEWS:
        raise ConfigError(f"view {view!r} is not allowed in public-safe configs")

    metric = config["metric"]
    if metric not in ALLOWED_METRICS:
        allowed = ", ".join(sorted(ALLOWED_METRICS))
        raise ConfigError(f"invalid metric: {metric!r}; allowed: {allowed}")

    _validate_inputs(config["inputs"])
    _validate_outputs(config.get("outputs", {}))
    _validate_safety(config.get("safety", {}), public_safe=public_safe)


def _validate_inputs(inputs: Any) -> None:
    if not isinstance(inputs, dict) or not inputs:
        raise ConfigError("inputs must be a non-empty object")
    for key, value in inputs.items():
        if not isinstance(key, str) or not key:
            raise ConfigError("input keys must be non-empty strings")
        if not isinstance(value, str) or not value:
            raise ConfigError(f"input {key!r} must be a non-empty path string")


def _validate_outputs(outputs: Any) -> None:
    if outputs is None:
        return
    if not isinstance(outputs, dict):
        raise ConfigError("outputs must be an object when present")
    for key, value in outputs.items():
        if not isinstance(key, str) or not key:
            raise ConfigError("output keys must be non-empty strings")
        if not isinstance(value, str) or not value:
            raise ConfigError(f"output {key!r} must be a non-empty path string")


def _validate_safety(safety: Any, *, public_safe: bool) -> None:
    if safety is None:
        return
    if not isinstance(safety, dict):
        raise ConfigError("safety must be an object when present")
    if public_safe:
        if safety.get("contains_raw_trace") is True:
            raise ConfigError("public-safe config must not contain raw traces")
        if safety.get("contains_secret_equivalent") is True:
            raise ConfigError("public-safe config must not contain secret-equivalent material")


def config_summary(config: dict[str, Any]) -> dict[str, Any]:
    """Return a compact JSON-serializable config summary."""

    return {
        "experiment_id": config["experiment_id"],
        "experiment_type": config["experiment_type"],
        "target": config["target"],
        "view": config["view"],
        "metric": config["metric"],
        "input_count": len(config.get("inputs", {})),
        "output_count": len(config.get("outputs", {})),
    }
