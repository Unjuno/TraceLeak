"""Render model sequence NN-vs-baseline comparison results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ModelSequenceComparisonReportingError(ValueError):
    """Raised when a comparison result cannot be rendered."""


BOUNDARY_REPORT_KEYS = (
    "validation_scope",
    "actual_trace_derived",
    "trace_collection_mode",
    "raw_secret_captured",
    "target_version",
    "source_pin",
    "build_id",
    "public_safe",
)


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


def model_sequence_comparison_report_dict(
    result: dict[str, Any],
    *,
    controls: list[dict[str, Any]] | None = None,
    expected_attribution_tokens: list[str] | None = None,
) -> dict[str, Any]:
    """Return a normalized report dictionary for a comparison result."""

    validate_model_sequence_comparison(result)
    controls = controls or []
    for control in controls:
        validate_model_sequence_comparison(control)

    baseline_accuracy = float(result["baseline"]["leave_one_out_nearest_neighbor_accuracy"])
    neural_accuracy = float(result["neural"]["leave_one_out_accuracy"])
    delta_accuracy = float(result["delta"]["accuracy_vs_nearest_neighbor"])
    control_warning = _control_warning(result)
    control_summary = control_summary_dict(controls) if controls else None
    neural = result.get("neural", {})
    top_attributions = list(neural.get("top_attributions", []))
    expected_tokens = list(expected_attribution_tokens or [])
    attribution_matches = expected_attribution_matches(top_attributions, expected_tokens)

    report = {
        "report_type": "model_sequence_nn_comparison_report",
        "target": result["target"],
        "view": result["view"],
        "label_name": result.get("label_name", "label"),
        "example_count": int(result["example_count"]),
        "baseline_accuracy": baseline_accuracy,
        "neural_accuracy": neural_accuracy,
        "neural_model_name": str(neural.get("model_name", "sparse-softmax-model-sequence-nn")),
        "neural_architecture": str(neural.get("architecture", "single-layer-softmax")),
        "delta_accuracy": delta_accuracy,
        "interpretation": result["interpretation"],
        "evidence_status": evidence_status(result["interpretation"], control_summary),
        "attribution_status": attribution_status(top_attributions, expected_tokens),
        "expected_attribution_tokens": expected_tokens,
        "attribution_matches": attribution_matches,
        "control_warning": control_warning,
        "top_attributions": top_attributions,
        "notes": list(result.get("notes", [])),
    }
    for key in BOUNDARY_REPORT_KEYS:
        if key in result:
            report[key] = result[key]
    if control_summary:
        report["control_summary"] = control_summary
    return report


def control_summary_dict(controls: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize multiple control comparison results."""

    if not controls:
        raise ModelSequenceComparisonReportingError("at least one control comparison is required")
    for control in controls:
        validate_model_sequence_comparison(control)

    neural_accuracies = [float(item["neural"]["leave_one_out_accuracy"]) for item in controls]
    baseline_accuracies = [
        float(item["baseline"]["leave_one_out_nearest_neighbor_accuracy"]) for item in controls
    ]
    max_neural = max(neural_accuracies)
    mean_neural = sum(neural_accuracies) / len(neural_accuracies)
    status = "control_pass" if max_neural <= 0.25 and mean_neural <= 0.25 else "control_attention"
    return {
        "control_count": len(controls),
        "max_neural_accuracy": max_neural,
        "mean_neural_accuracy": mean_neural,
        "max_baseline_accuracy": max(baseline_accuracies),
        "mean_baseline_accuracy": sum(baseline_accuracies) / len(baseline_accuracies),
        "status": status,
        "targets": [str(item.get("target", "unknown")) for item in controls],
    }


def evidence_status(interpretation: str, control_summary: dict[str, Any] | None) -> str:
    """Classify whether a positive NN comparison has required control evidence."""

    if interpretation != "neural_better":
        return "no_neural_advantage"
    if control_summary is None:
        return "controls_missing"
    if control_summary.get("status") != "control_pass":
        return "control_attention_required"
    return "candidate_signal_control_checked"


def attribution_status(
    top_attributions: list[dict[str, Any]],
    expected_attribution_tokens: list[str],
) -> str:
    """Classify whether expected source-level tokens appear in NN attributions."""

    if not expected_attribution_tokens:
        return "expected_attributions_not_declared"
    if not top_attributions:
        return "attributions_missing"
    if expected_attribution_matches(top_attributions, expected_attribution_tokens):
        return "expected_attribution_observed"
    return "expected_attribution_missing"


def expected_attribution_matches(
    top_attributions: list[dict[str, Any]],
    expected_attribution_tokens: list[str],
) -> list[str]:
    """Return expected attribution tokens observed in top NN attributions."""

    observed = {str(item.get("group_id", "")) for item in top_attributions}
    return [token for token in expected_attribution_tokens if token in observed]


def model_sequence_comparison_report_markdown(report: dict[str, Any]) -> str:
    """Render a model sequence comparison report as Markdown."""

    neural_label = report.get("neural_model_name", "sparse-softmax-model-sequence-nn")
    neural_architecture = report.get("neural_architecture", "single-layer-softmax")
    lines = [
        "# TraceLeak Model Sequence NN Comparison Report",
        "",
        f"- Target: `{report['target']}`",
        f"- View: `{report['view']}`",
        f"- Label: `{report['label_name']}`",
        f"- Examples: `{report['example_count']}`",
        f"- Neural model: `{neural_label}`",
        f"- Neural architecture: `{neural_architecture}`",
    ]
    if "validation_scope" in report:
        lines.extend(
            [
                f"- Validation scope: `{report['validation_scope']}`",
                f"- Actual trace derived: `{_markdown_bool(report.get('actual_trace_derived'))}`",
                f"- Trace collection mode: `{report.get('trace_collection_mode', 'unknown')}`",
                f"- Raw secret captured: `{_markdown_bool(report.get('raw_secret_captured'))}`",
            ]
        )
    if report.get("actual_trace_derived"):
        lines.extend(
            [
                f"- Target version: `{report.get('target_version', 'unknown')}`",
                f"- Source pin: `{report.get('source_pin', 'unknown')}`",
                f"- Build ID: `{report.get('build_id', 'unknown')}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Scores",
            "",
            "| Evaluator | Leave-one-out accuracy |",
            "|---|---:|",
            f"| Nearest-neighbor baseline | {report['baseline_accuracy']:.6g} |",
            f"| {neural_label} | {report['neural_accuracy']:.6g} |",
            "",
            "## Delta",
            "",
            f"- Accuracy delta vs nearest-neighbor: `{report['delta_accuracy']:.6g}`",
            f"- Interpretation: `{report['interpretation']}`",
            f"- Evidence status: `{report.get('evidence_status', 'unknown')}`",
            f"- Attribution status: `{report.get('attribution_status', 'unknown')}`",
            f"- Control warning: `{report['control_warning']}`",
        ]
    )

    expected_tokens = report.get("expected_attribution_tokens") or []
    if expected_tokens:
        lines.extend(["", "## Expected Attribution Tokens", ""])
        lines.extend(f"- `{token}`" for token in expected_tokens)
        matches = report.get("attribution_matches") or []
        lines.extend(["", "## Attribution Matches", ""])
        if matches:
            lines.extend(f"- `{token}`" for token in matches)
        else:
            lines.append("- `none`")

    top_attributions = report.get("top_attributions") or []
    if top_attributions:
        lines.extend(
            [
                "",
                "## Top NN Attributions",
                "",
                "| Rank | Token | Type | Score | Evidence |",
                "|---:|---|---|---:|---|",
            ]
        )
        for rank, item in enumerate(top_attributions[:10], start=1):
            evidence = ", ".join(item.get("evidence") or [])
            lines.append(
                "| {rank} | `{token}` | `{typ}` | {score:.6g} | {evidence} |".format(
                    rank=rank,
                    token=item.get("group_id", "unknown"),
                    typ=item.get("group_type", "unknown"),
                    score=float(item.get("score", 0.0)),
                    evidence=evidence,
                )
            )

    control_summary = report.get("control_summary")
    if control_summary:
        lines.extend(
            [
                "",
                "## Control Summary",
                "",
                f"- Control count: `{control_summary['control_count']}`",
                f"- Max control NN accuracy: `{control_summary['max_neural_accuracy']:.6g}`",
                f"- Mean control NN accuracy: `{control_summary['mean_neural_accuracy']:.6g}`",
                f"- Max control baseline accuracy: `{control_summary['max_baseline_accuracy']:.6g}`",
                f"- Mean control baseline accuracy: `{control_summary['mean_baseline_accuracy']:.6g}`",
                f"- Status: `{control_summary['status']}`",
            ]
        )

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


def _markdown_bool(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).lower()
