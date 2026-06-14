"""Compact metrics helpers for metadata demo outputs."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

METADATA_DEMO_METRICS_FORMAT = "traceleak.metadata_demo_metrics.v1"
METADATA_DEMO_METRICS_PHASE = "P66"
CSV_COLUMNS = [
    "format",
    "phase",
    "sample_id",
    "sample_digest",
    "source_pin_digest",
    "record_count",
    "label_count",
    "baseline_majority_accuracy",
    "baseline_nearest_neighbor_accuracy",
    "nn_accuracy",
    "nn_attribution_count",
    "metadata_only",
    "public_safe",
    "demo_claim_only",
]


class MetadataDemoMetricsError(ValueError):
    """Raised when compact demo metrics inputs are invalid."""


def build_metadata_demo_metrics(
    *,
    summary: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact deterministic metrics object from demo summary and manifest."""

    _require_summary(summary)
    _require_manifest(manifest, summary=summary)
    label_distribution = _dict(summary.get("label_distribution"), "summary.label_distribution")
    baseline_summary = _dict(summary.get("baseline_summary"), "summary.baseline_summary")
    nn_summary = _dict(summary.get("nn_summary"), "summary.nn_summary")
    flags = _dict(summary.get("flags"), "summary.flags")
    metrics = {
        "format": METADATA_DEMO_METRICS_FORMAT,
        "phase": METADATA_DEMO_METRICS_PHASE,
        "sample_id": summary["sample_id"],
        "sample_digest": summary["sample_digest"],
        "source_pin_digest": summary["source_pin_digest"],
        "record_count": summary["record_count"],
        "label_count": len(label_distribution),
        "label_distribution": dict(sorted(label_distribution.items())),
        "baseline_majority_accuracy": baseline_summary["majority_accuracy"],
        "baseline_nearest_neighbor_accuracy": baseline_summary["nearest_neighbor_accuracy"],
        "nn_accuracy": nn_summary["accuracy"],
        "nn_attribution_count": nn_summary["attribution_count"],
        "metadata_only": flags["metadata_only"],
        "public_safe": flags["public_safe"],
        "demo_claim_only": not flags["openssl_leakage_claim"],
    }
    validate_metadata_demo_metrics(metrics)
    return metrics


def build_metadata_demo_metrics_from_artifacts(artifacts: dict[str, Any]) -> dict[str, Any]:
    """Build compact metrics directly from metadata demo chain artifacts."""

    return build_metadata_demo_metrics(
        summary=_dict(artifacts.get("demo_summary"), "artifacts.demo_summary"),
        manifest=_dict(artifacts.get("demo_manifest"), "artifacts.demo_manifest"),
    )


def render_metadata_demo_metrics_csv(metrics: dict[str, Any]) -> str:
    """Render compact metrics as a one-row CSV."""

    validate_metadata_demo_metrics(metrics)
    row = {key: metrics[key] for key in CSV_COLUMNS}
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerow(row)
    return buffer.getvalue()


def write_metadata_demo_metrics_json(path: Path, metrics: dict[str, Any]) -> None:
    """Write compact metrics JSON."""

    validate_metadata_demo_metrics(metrics)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_metadata_demo_metrics_csv(path: Path, metrics: dict[str, Any]) -> None:
    """Write compact metrics CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_metadata_demo_metrics_csv(metrics), encoding="utf-8")


def validate_metadata_demo_metrics(metrics: dict[str, Any]) -> None:
    """Validate compact metadata demo metrics."""

    _eq(metrics.get("format"), METADATA_DEMO_METRICS_FORMAT, "metrics.format")
    _eq(metrics.get("phase"), METADATA_DEMO_METRICS_PHASE, "metrics.phase")
    for field in ["sample_id", "sample_digest", "source_pin_digest"]:
        _non_empty(metrics.get(field), f"metrics.{field}")
    _positive_int(metrics.get("record_count"), "metrics.record_count")
    _positive_int(metrics.get("label_count"), "metrics.label_count")
    for field in [
        "baseline_majority_accuracy",
        "baseline_nearest_neighbor_accuracy",
        "nn_accuracy",
    ]:
        _score(metrics.get(field), f"metrics.{field}")
    _positive_int(metrics.get("nn_attribution_count"), "metrics.nn_attribution_count", allow_zero=True)
    _eq(metrics.get("metadata_only"), True, "metrics.metadata_only")
    _eq(metrics.get("public_safe"), True, "metrics.public_safe")
    _eq(metrics.get("demo_claim_only"), True, "metrics.demo_claim_only")
    labels = _dict(metrics.get("label_distribution"), "metrics.label_distribution")
    if len(labels) != metrics["label_count"]:
        raise MetadataDemoMetricsError("metrics.label_count must match label_distribution")


def _require_summary(summary: dict[str, Any]) -> None:
    _eq(
        summary.get("format"),
        "traceleak.openssl_model_sequence_metadata_sample_demo_result.v1",
        "summary.format",
    )
    _non_empty(summary.get("sample_id"), "summary.sample_id")
    _non_empty(summary.get("sample_digest"), "summary.sample_digest")
    _non_empty(summary.get("source_pin_digest"), "summary.source_pin_digest")
    _positive_int(summary.get("record_count"), "summary.record_count")
    flags = _dict(summary.get("flags"), "summary.flags")
    _eq(flags.get("metadata_only"), True, "summary.flags.metadata_only")
    _eq(flags.get("public_safe"), True, "summary.flags.public_safe")
    _eq(flags.get("openssl_leakage_claim"), False, "summary.flags.openssl_leakage_claim")


def _require_manifest(manifest: dict[str, Any], *, summary: dict[str, Any]) -> None:
    _eq(manifest.get("format"), "traceleak.openssl_model_sequence_metadata_demo_manifest.v1", "manifest.format")
    for field in ["sample_id", "sample_digest", "source_pin_digest"]:
        _eq(manifest.get(field), summary[field], f"manifest.{field}")


def _dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MetadataDemoMetricsError(f"{name} must be an object")
    return value


def _non_empty(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise MetadataDemoMetricsError(f"{name} must be a non-empty string")


def _positive_int(value: Any, name: str, *, allow_zero: bool = False) -> None:
    if not isinstance(value, int):
        raise MetadataDemoMetricsError(f"{name} must be an integer")
    if allow_zero:
        if value < 0:
            raise MetadataDemoMetricsError(f"{name} must be non-negative")
    elif value <= 0:
        raise MetadataDemoMetricsError(f"{name} must be positive")


def _score(value: Any, name: str) -> None:
    if not isinstance(value, int | float):
        raise MetadataDemoMetricsError(f"{name} must be numeric")
    if value < 0 or value > 1:
        raise MetadataDemoMetricsError(f"{name} must be between 0 and 1")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise MetadataDemoMetricsError(f"{name} must be {expected!r}")
