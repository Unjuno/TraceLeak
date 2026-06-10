"""Reporting helpers for TraceLeak results."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from traceleak.attribution import AttributionScore


def attribution_report_dict(
    *,
    target: str,
    view: str,
    metric: str,
    score: float,
    attributions: Iterable[AttributionScore],
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Build a JSON-serializable attribution report."""

    return {
        "target": target,
        "view": view,
        "metric": metric,
        "score": score,
        "attributions": [asdict(item) for item in attributions],
        "notes": notes or [],
    }


def write_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write a report dictionary as formatted JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def attribution_report_markdown(report: dict[str, Any], *, top_n: int = 10) -> str:
    """Render a compact attribution report as Markdown."""

    lines = [
        "# TraceLeak Attribution Report",
        "",
        f"- Target: `{report['target']}`",
        f"- View: `{report['view']}`",
        f"- Metric: `{report['metric']}`",
        f"- Score: `{report['score']}`",
        "",
        "## Top Attribution Scores",
        "",
        "| Rank | Group | Type | Contribution | Location | Evidence |",
        "|---:|---|---|---:|---|---|",
    ]

    attributions = report.get("attributions", [])[:top_n]
    for index, item in enumerate(attributions, start=1):
        evidence = ", ".join(item.get("evidence") or [])
        location = item.get("location") or ""
        lines.append(
            "| {rank} | `{group}` | `{typ}` | {contribution:.6g} | `{location}` | {evidence} |".format(
                rank=index,
                group=item["group_id"],
                typ=item["group_type"],
                contribution=item["contribution"],
                location=location,
                evidence=evidence,
            )
        )

    notes = report.get("notes") or []
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)

    lines.append("")
    return "\n".join(lines)


def write_report_markdown(path: str | Path, report: dict[str, Any], *, top_n: int = 10) -> None:
    """Write a report dictionary as Markdown."""

    Path(path).write_text(attribution_report_markdown(report, top_n=top_n), encoding="utf-8")
