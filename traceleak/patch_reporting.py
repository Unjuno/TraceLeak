"""Render patch verification results as Markdown or JSON reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.patch_verification import (
    patch_verification_summary,
    validate_patch_verification,
)


def patch_verification_report_dict(result: dict[str, Any], *, public_safe: bool = True) -> dict[str, Any]:
    """Create a normalized patch verification report dictionary."""

    validate_patch_verification(result, public_safe=public_safe)
    summary = patch_verification_summary(result)
    return {
        "report_type": "patch_verification",
        "verification_id": summary["verification_id"],
        "target": summary["target"],
        "view": summary["view"],
        "metric": summary["metric"],
        "before": result["before"],
        "after": result["after"],
        "delta": summary["delta"],
        "status": summary["status"],
        "changed_groups": result.get("changed_groups", []),
        "notes": result.get("notes", []),
    }


def patch_verification_report_markdown(report: dict[str, Any]) -> str:
    """Render a normalized patch verification report as Markdown."""

    lines = [
        "# TraceLeak Patch Verification Report",
        "",
        f"- Verification ID: `{report['verification_id']}`",
        f"- Target: `{report['target']}`",
        f"- View: `{report['view']}`",
        f"- Metric: `{report['metric']}`",
        f"- Status: `{report['status']}`",
        f"- Delta: `{report['delta']:.6g}`",
        "",
        "## Before / After",
        "",
        "| Snapshot | Run ID | Score | Report |",
        "|---|---|---:|---|",
        _measurement_row("before", report["before"]),
        _measurement_row("after", report["after"]),
    ]

    changed_groups = report.get("changed_groups", [])
    if changed_groups:
        lines.extend(
            [
                "",
                "## Changed Groups",
                "",
                "| Group | Location | Before | After | Delta |",
                "|---|---|---:|---:|---:|",
            ]
        )
        for item in changed_groups:
            before = item.get("before_contribution")
            after = item.get("after_contribution")
            delta = _changed_group_delta(before, after)
            lines.append(
                "| `{group}` | `{location}` | {before} | {after} | {delta} |".format(
                    group=item.get("group_id", ""),
                    location=item.get("location", ""),
                    before=_format_number_or_blank(before),
                    after=_format_number_or_blank(after),
                    delta=_format_number_or_blank(delta),
                )
            )

    notes = report.get("notes", [])
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)

    lines.append("")
    return "\n".join(lines)


def write_patch_verification_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write a normalized patch verification report as JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_patch_verification_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write a normalized patch verification report as Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(patch_verification_report_markdown(report), encoding="utf-8")


def _measurement_row(label: str, measurement: dict[str, Any]) -> str:
    report_path = measurement.get("report", "")
    return "| `{label}` | `{run_id}` | {score:.6g} | `{report}` |".format(
        label=label,
        run_id=measurement["run_id"],
        score=measurement["score"],
        report=report_path,
    )


def _changed_group_delta(before: Any, after: Any) -> float | None:
    if isinstance(before, int | float) and isinstance(after, int | float):
        return float(before) - float(after)
    return None


def _format_number_or_blank(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{float(value):.6g}"
    return ""
