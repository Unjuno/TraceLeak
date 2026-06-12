"""Render model sequence NN-vs-baseline comparison results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ModelSequenceComparisonReportingError(ValueError):
    """Raised when a comparison result cannot be rendered."""


def load_model_sequence_comparison(path: str | Path) -> dict[str, Any]:
    """Load a model sequence comparison JSON file."""

    comparison_path = Path(path)
    if not comparison_path.exists():
        raise ModelSequenceComparisonReportingError(f"comparison file not found: {comparison_path}")
    try:
        payload = json.loads(comparison_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelSequenceComparisonReportingError(
            f"invalid JSON in {comparison_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise ModelSequenceComparisonReportingError("comparison input must be a JSON object")
    validate_model_sequence_comparison(payload)
    return payload


def validate_model_sequence_comparison(result: dict[str, Any]) -> None:
    """Validate the fields needed to render a compact comparison report."""

    required = [
        "result_type",
        "target",
        "view",
        "example_count",
        "baseline",
        "neural",
        "delta",
        "interpretation",
    ]
    for key in required:
        if key not in result:
            raise ModelSequenceComparisonReportingError(f"missing comparison field: {key}")
    if result["result_type"] != "model_sequence_nn_vs_baseline":
        raise ModelSequenceComparisonReportingError(
            f"unsupported result_type: {result['result_type']!r}"
        )
    _require_number(result["example_count"], "example_count")
    _require_number(
        result["baseline"].get("leave_one_out_nearest_neighbor_accuracy"),
        "baseline.leave_one_out_nearest_neighbor_accuracy",
    )
    _require_number(result["neural"].get("leave_one_out_accuracy"), "neural.leave_one_out_accuracy")
    _require_number(result["delta"].get("accuracy_vs_nearest_neighbor"), "delta.accuracy")


def model_sequence_comparison_report_dict(result: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized report dictionary for a comparison result."""

    validate_model_sequence_comparison(result)
    baseline_accuracy = float(result["baseline"]["leave_one_out_nearest_neighbor_accuracy"])
    neural_accuracy = float(result["neural"]["leave_one_out_accuracy"])
    delta_accuracy = float(result["delta"]["accuracy_vs_nearest_neighbor"])
    control_warning = _control_warning(result)

    return {
        "report_type": "model_sequence_nn_comparison_report",
        "target": result["target"],
        "view": result["view"],
        "label_name": result.get("label_name", "label"),
        "example_count": int(result["example_count"]),
        "baseline_accuracy": baseline_accuracy,
        "neural_accuracy": neural_accuracy,
        "delta_accuracy": delta_accuracy,
        "interpretation": result["interpretation"],
        "control_warning": control_warning,
        "notes": list(result.get("notes", [])),
    }


def model_sequence_comparison_report_markdown(report: dict[str, Any]) -> str:
    """Render a model sequence comparison report as Markdown."""

    lines = [
        "# TraceLeak Model Sequence NN Comparison Report",
        "",
        f"- Target: `{report['target']}`",
        f"- View: `{report['view']}`",
        f"- Label: `{report['label_name']}`",
        f"- Examples: `{report['example_count']}`",
        "",
        "## Scores",
        "",
        "| Evaluator | Leave-one-out accuracy |",
        "|---|---:|",
        f"| Nearest-neighbor baseline | {report['baseline_accuracy']:.6g} |",
        f"| Sparse-softmax NN | {report['neural_accuracy']:.6g} |",
        "",
        "## Delta",
        "",
        f"- Accuracy delta vs nearest-neighbor: `{report['delta_accuracy']:.6g}`",
        f"- Interpretation: `{report['interpretation']}`",
        f"- Control warning: `{report['control_warning']}`",
    ]

    notes = report.get("notes") or []
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)

    lines.append("")
    return "\n".join(lines)


def write_model_sequence_comparison_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write a comparison report dictionary as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_model_sequence_comparison_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write a comparison report dictionary as Markdown."""

    Path(path).write_text(model_sequence_comparison_report_markdown(report), encoding="utf-8")


def _control_warning(result: dict[str, Any]) -> str:
    target = str(result.get("target", "")).lower()
    label_name = str(result.get("label_name", "")).lower()
    neural_accuracy = float(result["neural"]["leave_one_out_accuracy"])
    if "control" not in target and "control" not in label_name and "shuffled" not in label_name:
        return "not_a_control_result"
    if neural_accuracy >= 0.75:
        return "control_accuracy_high"
    if neural_accuracy <= 0.25:
        return "control_accuracy_low"
    return "control_accuracy_near_chance"


def _require_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ModelSequenceComparisonReportingError(f"{name} must be a number")
