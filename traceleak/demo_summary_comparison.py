"""Compare metadata-only demo summary outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEMO_SUMMARY_COMPARISON_FORMAT = "traceleak.demo_summary_comparison.v1"
DEMO_SUMMARY_COMPARISON_PHASE = "P87"
METADATA_DEMO_FORMAT = "traceleak.openssl_model_sequence_metadata_sample_demo_result.v1"
SYMBOLIC_DEMO_FORMAT = "traceleak.symbolic_metadata_demo_chain.v1"


class DemoSummaryComparisonError(ValueError):
    """Raised when demo summary comparison inputs are invalid."""


def build_demo_summary_comparison(
    *,
    metadata_summary: dict[str, Any],
    symbolic_summary: dict[str, Any],
) -> dict[str, Any]:
    """Compare metadata-demo and authored symbolic-demo summary JSON objects."""

    _require_metadata_summary(metadata_summary)
    _require_symbolic_summary(symbolic_summary)
    metadata_metrics = _extract_metrics(metadata_summary)
    symbolic_metrics = _extract_metrics(symbolic_summary)
    comparison = {
        "format": DEMO_SUMMARY_COMPARISON_FORMAT,
        "phase": DEMO_SUMMARY_COMPARISON_PHASE,
        "mode": "metadata_only_demo_summary_comparison",
        "left": metadata_metrics,
        "right": symbolic_metrics,
        "deltas": {
            "record_count": symbolic_metrics["record_count"] - metadata_metrics["record_count"],
            "baseline_majority_accuracy": _delta(
                symbolic_metrics["baseline_majority_accuracy"],
                metadata_metrics["baseline_majority_accuracy"],
            ),
            "baseline_nearest_neighbor_accuracy": _delta(
                symbolic_metrics["baseline_nearest_neighbor_accuracy"],
                metadata_metrics["baseline_nearest_neighbor_accuracy"],
            ),
            "nn_accuracy": _delta(symbolic_metrics["nn_accuracy"], metadata_metrics["nn_accuracy"]),
            "nn_attribution_count": (
                symbolic_metrics["nn_attribution_count"] - metadata_metrics["nn_attribution_count"]
            ),
        },
        "label_sets_match": set(metadata_metrics["label_distribution"]) == set(symbolic_metrics["label_distribution"]),
        "flags": {
            "metadata_only": True,
            "payload_free": True,
            "public_safe": True,
            "openssl_leakage_claim": False,
        },
        "notes": [
            "Comparison of two metadata-only local demo summaries.",
            "This comparison does not claim or prove OpenSSL leakage.",
        ],
    }
    validate_demo_summary_comparison(comparison)
    return comparison


def render_demo_summary_comparison_markdown(comparison: dict[str, Any]) -> str:
    """Render a compact Markdown table for demo summary comparison."""

    validate_demo_summary_comparison(comparison)
    left = comparison["left"]
    right = comparison["right"]
    deltas = comparison["deltas"]
    lines = [
        "# Demo Summary Comparison",
        "",
        f"- Phase: `{comparison['phase']}`",
        f"- Mode: `{comparison['mode']}`",
        "- Scope: metadata-only local demo summaries",
        "",
        "| Metric | Metadata demo | Symbolic demo | Delta |",
        "|---|---:|---:|---:|",
        f"| Record count | `{left['record_count']}` | `{right['record_count']}` | `{deltas['record_count']}` |",
        f"| Baseline majority accuracy | `{left['baseline_majority_accuracy']}` | `{right['baseline_majority_accuracy']}` | `{deltas['baseline_majority_accuracy']}` |",
        f"| Baseline nearest-neighbor accuracy | `{left['baseline_nearest_neighbor_accuracy']}` | `{right['baseline_nearest_neighbor_accuracy']}` | `{deltas['baseline_nearest_neighbor_accuracy']}` |",
        f"| NN accuracy | `{left['nn_accuracy']}` | `{right['nn_accuracy']}` | `{deltas['nn_accuracy']}` |",
        f"| NN attribution count | `{left['nn_attribution_count']}` | `{right['nn_attribution_count']}` | `{deltas['nn_attribution_count']}` |",
        "",
        "## Labels",
        "",
        f"- Metadata demo labels: `{sorted(left['label_distribution'])}`",
        f"- Symbolic demo labels: `{sorted(right['label_distribution'])}`",
        f"- Label sets match: `{comparison['label_sets_match']}`",
        "",
        "## Safety flags",
        "",
        f"- metadata_only: `{comparison['flags']['metadata_only']}`",
        f"- payload_free: `{comparison['flags']['payload_free']}`",
        f"- public_safe: `{comparison['flags']['public_safe']}`",
        f"- demo claim only: `{not comparison['flags']['openssl_leakage_claim']}`",
        "",
        "## Notes",
        "",
        "Both inputs are metadata-only local demo summaries.",
        "This comparison is not OpenSSL leakage evidence.",
        "",
    ]
    markdown = "\n".join(lines)
    validate_demo_summary_comparison_markdown(markdown)
    return markdown


def validate_demo_summary_comparison(comparison: dict[str, Any]) -> None:
    """Validate a demo summary comparison object."""

    _eq(comparison.get("format"), DEMO_SUMMARY_COMPARISON_FORMAT, "comparison.format")
    _eq(comparison.get("phase"), DEMO_SUMMARY_COMPARISON_PHASE, "comparison.phase")
    _eq(
        comparison.get("mode"),
        "metadata_only_demo_summary_comparison",
        "comparison.mode",
    )
    left = _dict(comparison.get("left"), "comparison.left")
    right = _dict(comparison.get("right"), "comparison.right")
    _validate_metrics(left, "comparison.left")
    _validate_metrics(right, "comparison.right")
    deltas = _dict(comparison.get("deltas"), "comparison.deltas")
    for field in [
        "record_count",
        "baseline_majority_accuracy",
        "baseline_nearest_neighbor_accuracy",
        "nn_accuracy",
        "nn_attribution_count",
    ]:
        if field not in deltas:
            raise DemoSummaryComparisonError(f"comparison.deltas.{field} is required")
    if not isinstance(comparison.get("label_sets_match"), bool):
        raise DemoSummaryComparisonError("comparison.label_sets_match must be boolean")
    flags = _dict(comparison.get("flags"), "comparison.flags")
    for key in ["metadata_only", "payload_free", "public_safe"]:
        _eq(flags.get(key), True, f"comparison.flags.{key}")
    _eq(flags.get("openssl_leakage_claim"), False, "comparison.flags.openssl_leakage_claim")


def validate_demo_summary_comparison_markdown(markdown: str) -> None:
    """Validate comparison Markdown shape."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise DemoSummaryComparisonError("markdown must be a newline-terminated string")
    for text in [
        "# Demo Summary Comparison",
        "| Metric | Metadata demo | Symbolic demo | Delta |",
        "## Labels",
        "## Safety flags",
        "## Notes",
        "This comparison is not OpenSSL leakage evidence.",
    ]:
        if text not in markdown:
            raise DemoSummaryComparisonError(f"missing markdown text: {text}")


def write_demo_summary_comparison_json(path: Path, comparison: dict[str, Any]) -> None:
    """Write demo summary comparison JSON."""

    validate_demo_summary_comparison(comparison)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_demo_summary_comparison_markdown(path: Path, markdown: str) -> None:
    """Write demo summary comparison Markdown."""

    validate_demo_summary_comparison_markdown(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _require_metadata_summary(summary: dict[str, Any]) -> None:
    _eq(summary.get("format"), METADATA_DEMO_FORMAT, "metadata_summary.format")
    _validate_summary_common(summary, "metadata_summary")


def _require_symbolic_summary(summary: dict[str, Any]) -> None:
    _eq(summary.get("format"), SYMBOLIC_DEMO_FORMAT, "symbolic_summary.format")
    _validate_summary_common(summary, "symbolic_summary")


def _validate_summary_common(summary: dict[str, Any], name: str) -> None:
    if not isinstance(summary.get("record_count"), int) or summary["record_count"] <= 0:
        raise DemoSummaryComparisonError(f"{name}.record_count must be positive")
    if not isinstance(summary.get("label_distribution"), dict) or len(summary["label_distribution"]) < 2:
        raise DemoSummaryComparisonError(f"{name}.label_distribution must contain at least two labels")
    baseline = _dict(summary.get("baseline_summary"), f"{name}.baseline_summary")
    nn = _dict(summary.get("nn_summary"), f"{name}.nn_summary")
    _score(baseline.get("majority_accuracy"), f"{name}.baseline_summary.majority_accuracy")
    _score(
        baseline.get("nearest_neighbor_accuracy"),
        f"{name}.baseline_summary.nearest_neighbor_accuracy",
    )
    _score(nn.get("accuracy"), f"{name}.nn_summary.accuracy")
    if not isinstance(nn.get("attribution_count"), int) or nn["attribution_count"] < 0:
        raise DemoSummaryComparisonError(f"{name}.nn_summary.attribution_count must be non-negative")
    flags = _dict(summary.get("flags"), f"{name}.flags")
    for key in ["metadata_only", "payload_free", "public_safe"]:
        _eq(flags.get(key), True, f"{name}.flags.{key}")
    _eq(flags.get("openssl_leakage_claim"), False, f"{name}.flags.openssl_leakage_claim")


def _extract_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "format": summary["format"],
        "record_count": summary["record_count"],
        "label_distribution": dict(sorted(summary["label_distribution"].items())),
        "baseline_majority_accuracy": summary["baseline_summary"]["majority_accuracy"],
        "baseline_nearest_neighbor_accuracy": summary["baseline_summary"]["nearest_neighbor_accuracy"],
        "nn_accuracy": summary["nn_summary"]["accuracy"],
        "nn_attribution_count": summary["nn_summary"]["attribution_count"],
    }


def _validate_metrics(metrics: dict[str, Any], name: str) -> None:
    if not isinstance(metrics.get("format"), str) or not metrics["format"]:
        raise DemoSummaryComparisonError(f"{name}.format must be a non-empty string")
    if not isinstance(metrics.get("record_count"), int) or metrics["record_count"] <= 0:
        raise DemoSummaryComparisonError(f"{name}.record_count must be positive")
    labels = _dict(metrics.get("label_distribution"), f"{name}.label_distribution")
    if len(labels) < 2:
        raise DemoSummaryComparisonError(f"{name}.label_distribution must contain at least two labels")
    for field in [
        "baseline_majority_accuracy",
        "baseline_nearest_neighbor_accuracy",
        "nn_accuracy",
    ]:
        _score(metrics.get(field), f"{name}.{field}")
    if not isinstance(metrics.get("nn_attribution_count"), int) or metrics["nn_attribution_count"] < 0:
        raise DemoSummaryComparisonError(f"{name}.nn_attribution_count must be non-negative")


def _delta(right: float, left: float) -> float:
    return round(float(right) - float(left), 12)


def _score(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or value < 0 or value > 1:
        raise DemoSummaryComparisonError(f"{name} must be a score between 0 and 1")


def _dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DemoSummaryComparisonError(f"{name} must be an object")
    return value


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise DemoSummaryComparisonError(f"{name} must be {expected!r}")
