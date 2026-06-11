"""Public-safe comparison report helpers for TraceLeak.

Comparison reports summarize two public-safe measurements, for example a leak
condition versus a control condition, or a model result versus a baseline.
"""

from __future__ import annotations

import json
from math import isfinite
from pathlib import Path
from typing import Any

from traceleak.schema import PUBLIC_SAFE_VIEWS, SECRET_EQUIVALENT_KEYS

ALLOWED_COMPARISON_STATUSES: set[str] = {
    "higher",
    "lower",
    "unchanged",
    "inconclusive",
}


class ComparisonError(ValueError):
    """Raised when a comparison input is invalid."""


def load_comparison(path: str | Path) -> dict[str, Any]:
    """Load a comparison JSON file."""

    comparison_path = Path(path)
    if not comparison_path.exists():
        raise ComparisonError(f"comparison file not found: {comparison_path}")
    try:
        return json.loads(comparison_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ComparisonError(f"invalid JSON in {comparison_path}: {exc}") from exc


def comparison_delta(left_score: float, right_score: float) -> float:
    """Return left-right score delta."""

    _require_number(left_score, "left_score")
    _require_number(right_score, "right_score")
    return left_score - right_score


def classify_comparison(delta: float, *, tolerance: float = 1e-9) -> str:
    """Classify a comparison delta."""

    _require_number(delta, "delta")
    _require_number(tolerance, "tolerance")
    if tolerance < 0:
        raise ComparisonError("tolerance must be non-negative")
    if delta > tolerance:
        return "higher"
    if delta < -tolerance:
        return "lower"
    return "unchanged"


def validate_comparison(data: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate a comparison dictionary."""

    for key in ("comparison_id", "comparison_type", "target", "view", "metric", "left", "right"):
        if key not in data:
            raise ComparisonError(f"missing required comparison field: {key}")

    _require_non_empty_string(data["comparison_id"], "comparison_id")
    _require_non_empty_string(data["comparison_type"], "comparison_type")
    _require_non_empty_string(data["target"], "target")
    _require_non_empty_string(data["metric"], "metric")

    view = data["view"]
    _require_non_empty_string(view, "view")
    if public_safe and view not in PUBLIC_SAFE_VIEWS:
        raise ComparisonError(f"view {view!r} is not allowed in public-safe comparisons")

    _validate_measurement(data["left"], "left")
    _validate_measurement(data["right"], "right")

    computed_delta = comparison_delta(data["left"]["score"], data["right"]["score"])
    if "delta" in data:
        _require_number(data["delta"], "delta")
        if abs(float(data["delta"]) - computed_delta) > 1e-9:
            raise ComparisonError("delta does not match left.score - right.score")

    if "status" in data and data["status"] not in ALLOWED_COMPARISON_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_COMPARISON_STATUSES))
        raise ComparisonError(f"invalid status: {data['status']!r}; allowed: {allowed}")

    _reject_secret_equivalent_fields(data)


def comparison_report_dict(data: dict[str, Any], *, public_safe: bool = True) -> dict[str, Any]:
    """Return a normalized comparison report dictionary."""

    validate_comparison(data, public_safe=public_safe)
    delta = comparison_delta(data["left"]["score"], data["right"]["score"])
    status = data.get("status") or classify_comparison(delta)
    return {
        "report_type": "comparison",
        "comparison_id": data["comparison_id"],
        "comparison_type": data["comparison_type"],
        "target": data["target"],
        "view": data["view"],
        "metric": data["metric"],
        "left": data["left"],
        "right": data["right"],
        "delta": delta,
        "status": status,
        "interpretation": data.get("interpretation", ""),
        "notes": data.get("notes", []),
    }


def comparison_report_markdown(report: dict[str, Any]) -> str:
    """Render a normalized comparison report as Markdown."""

    lines = [
        "# TraceLeak Comparison Report",
        "",
        f"- Comparison ID: `{report['comparison_id']}`",
        f"- Type: `{report['comparison_type']}`",
        f"- Target: `{report['target']}`",
        f"- View: `{report['view']}`",
        f"- Metric: `{report['metric']}`",
        f"- Status: `{report['status']}`",
        f"- Delta: `{report['delta']:.6g}`",
        "",
        "## Measurements",
        "",
        "| Side | Label | Score | Report |",
        "|---|---|---:|---|",
        _measurement_row("left", report["left"]),
        _measurement_row("right", report["right"]),
    ]

    if report.get("interpretation"):
        lines.extend(["", "## Interpretation", "", report["interpretation"]])

    notes = report.get("notes", [])
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)

    lines.append("")
    return "\n".join(lines)


def write_comparison_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write a normalized comparison report as JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_comparison_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write a normalized comparison report as Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(comparison_report_markdown(report), encoding="utf-8")


def _measurement_row(side: str, measurement: dict[str, Any]) -> str:
    return "| `{side}` | `{label}` | {score:.6g} | `{report}` |".format(
        side=side,
        label=measurement["label"],
        score=measurement["score"],
        report=measurement.get("report", ""),
    )


def _validate_measurement(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        raise ComparisonError(f"{name} must be an object")
    _require_non_empty_string(value.get("label"), f"{name}.label")
    _require_number(value.get("score"), f"{name}.score")
    if "report" in value:
        _require_non_empty_string(value["report"], f"{name}.report")


def _require_non_empty_string(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ComparisonError(f"{name} must be a non-empty string")


def _require_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool) or not isfinite(value):
        raise ComparisonError(f"{name} must be a finite number")


def _reject_secret_equivalent_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in SECRET_EQUIVALENT_KEYS:
                raise ComparisonError(f"secret-equivalent field is not allowed: {key}")
            _reject_secret_equivalent_fields(child)
    elif isinstance(value, list):
        for child in value:
            _reject_secret_equivalent_fields(child)
