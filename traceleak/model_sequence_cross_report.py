"""Render cross-target reports for model sequence NN comparisons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.model_sequence_comparison_reporting import (
    ModelSequenceComparisonReportingError,
    control_summary_dict,
    validate_model_sequence_comparison,
)


class ModelSequenceCrossReportError(ValueError):
    """Raised when a cross report cannot be built."""


def model_sequence_cross_report_dict(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a normalized cross-target comparison report."""

    if not entries:
        raise ModelSequenceCrossReportError("at least one comparison entry is required")

    rows: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for entry in entries:
        name = str(entry.get("name", "")).strip()
        if not name:
            raise ModelSequenceCrossReportError("entry name must not be empty")
        if name in seen_names:
            raise ModelSequenceCrossReportError(f"duplicate entry name: {name}")
        seen_names.add(name)

        comparison = entry.get("comparison")
        if not isinstance(comparison, dict):
            raise ModelSequenceCrossReportError(f"entry {name!r} comparison must be an object")
        try:
            validate_model_sequence_comparison(comparison)
        except ModelSequenceComparisonReportingError as exc:
            raise ModelSequenceCrossReportError(f"invalid comparison for {name}: {exc}") from exc

        controls = entry.get("controls") or []
        if not isinstance(controls, list):
            raise ModelSequenceCrossReportError(f"entry {name!r} controls must be a list")
        control_summary = control_summary_dict(controls) if controls else None

        baseline_accuracy = float(
            comparison["baseline"]["leave_one_out_nearest_neighbor_accuracy"]
        )
        neural_accuracy = float(comparison["neural"]["leave_one_out_accuracy"])
        delta_accuracy = float(comparison["delta"]["accuracy_vs_nearest_neighbor"])
        top_attributions = list(comparison.get("neural", {}).get("top_attributions", []))
        rows.append(
            {
                "name": name,
                "target": comparison["target"],
                "view": comparison["view"],
                "label_name": comparison.get("label_name", "label"),
                "example_count": int(comparison["example_count"]),
                "baseline_accuracy": baseline_accuracy,
                "neural_accuracy": neural_accuracy,
                "delta_accuracy": delta_accuracy,
                "interpretation": comparison["interpretation"],
                "control_status": control_summary["status"] if control_summary else "not_provided",
                "control_summary": control_summary,
                "top_attributions": top_attributions[:5],
            }
        )

    return {
        "report_type": "model_sequence_cross_report",
        "entry_count": len(rows),
        "rows": rows,
        "notes": [
            "Cross report compares NN-vs-baseline results across public-safe model sequence samples.",
            "Positive NN deltas are design evidence, not proof of real cryptographic leakage.",
        ],
    }


def model_sequence_cross_report_markdown(report: dict[str, Any]) -> str:
    """Render a cross-target comparison report as Markdown."""

    rows = report.get("rows") or []
    lines = [
        "# TraceLeak Model Sequence Cross Report",
        "",
        "## Summary",
        "",
        "| Entry | Target | Examples | Nearest-neighbor | Sparse-softmax NN | Delta | Interpretation | Control |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {name} | `{target}` | {examples} | {baseline:.6g} | {neural:.6g} | {delta:.6g} | `{interp}` | `{control}` |".format(
                name=row["name"],
                target=row["target"],
                examples=row["example_count"],
                baseline=float(row["baseline_accuracy"]),
                neural=float(row["neural_accuracy"]),
                delta=float(row["delta_accuracy"]),
                interp=row["interpretation"],
                control=row["control_status"],
            )
        )

    lines.extend(["", "## Attribution Alignment", ""])
    for row in rows:
        attributions = row.get("top_attributions") or []
        if attributions:
            tokens = "; ".join(f"`{item.get('group_id', 'unknown')}`" for item in attributions[:2])
        else:
            tokens = "`not_available`"
        lines.append(f"- {row['name']}: {tokens}")

    lines.extend(["", "## Control Details", ""])
    for row in rows:
        summary = row.get("control_summary")
        if not summary:
            lines.append(f"- {row['name']}: `not_provided`")
            continue
        lines.append(
            "- {name}: count=`{count}`, max_nn=`{max_nn:.6g}`, mean_nn=`{mean_nn:.6g}`, status=`{status}`".format(
                name=row["name"],
                count=summary["control_count"],
                max_nn=float(summary["max_neural_accuracy"]),
                mean_nn=float(summary["mean_neural_accuracy"]),
                status=summary["status"],
            )
        )

    notes = report.get("notes") or []
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)

    lines.append("")
    return "\n".join(lines)


def write_model_sequence_cross_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write a cross report as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_model_sequence_cross_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write a cross report as Markdown."""

    Path(path).write_text(model_sequence_cross_report_markdown(report), encoding="utf-8")
