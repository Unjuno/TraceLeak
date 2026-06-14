"""Markdown report helpers for authored symbolic metadata demo outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from traceleak.symbolic_metadata_demo_chain import validate_symbolic_metadata_demo_summary

SYMBOLIC_METADATA_DEMO_REPORT_PHASE = "P85"


class SymbolicMetadataDemoReportError(ValueError):
    """Raised when the symbolic metadata demo report is invalid."""


def render_symbolic_metadata_demo_report(summary: dict[str, Any]) -> str:
    """Render a compact Markdown report from authored symbolic demo summary."""

    validate_symbolic_metadata_demo_summary(summary)
    lines = [
        "# Symbolic Metadata Demo Report",
        "",
        f"- Phase: `{SYMBOLIC_METADATA_DEMO_REPORT_PHASE}`",
        f"- Demo phase: `{summary['phase']}`",
        f"- Mode: `{summary['mode']}`",
        f"- Target: `{summary['target']}`",
        f"- Record count: `{summary['record_count']}`",
        f"- Label name: `{summary['label_name']}`",
        "",
        "## Label distribution",
        "",
        "| Label | Count |",
        "|---|---:|",
    ]
    for label, count in sorted(summary["label_distribution"].items()):
        lines.append(f"| `{label}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Baseline",
            "",
            f"- Majority LOO accuracy: `{summary['baseline_summary']['majority_accuracy']}`",
            f"- Nearest-neighbor LOO accuracy: `{summary['baseline_summary']['nearest_neighbor_accuracy']}`",
            "",
            "## Neural model",
            "",
            f"- Model: `{summary['nn_summary']['model_name']}`",
            f"- LOO accuracy: `{summary['nn_summary']['accuracy']}`",
            f"- Attribution count: `{summary['nn_summary']['attribution_count']}`",
            "",
            "## Safety flags",
            "",
            f"- metadata_only: `{summary['flags']['metadata_only']}`",
            f"- payload_free: `{summary['flags']['payload_free']}`",
            f"- public_safe: `{summary['flags']['public_safe']}`",
            f"- demo claim only: `{not summary['flags']['openssl_leakage_claim']}`",
            "",
            "## Notes",
            "",
            "This report summarizes authored symbolic metadata-only local demo output.",
            "It is not OpenSSL leakage evidence.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    validate_symbolic_metadata_demo_report(markdown)
    return markdown


def validate_symbolic_metadata_demo_report(markdown: str) -> None:
    """Validate symbolic metadata demo report Markdown shape."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise SymbolicMetadataDemoReportError("markdown must be a newline-terminated string")
    for text in [
        "# Symbolic Metadata Demo Report",
        f"- Phase: `{SYMBOLIC_METADATA_DEMO_REPORT_PHASE}`",
        "## Label distribution",
        "## Baseline",
        "## Neural model",
        "## Safety flags",
        "## Notes",
        "It is not OpenSSL leakage evidence.",
    ]:
        if text not in markdown:
            raise SymbolicMetadataDemoReportError(f"missing report text: {text}")


def write_symbolic_metadata_demo_report(path: Path, markdown: str) -> None:
    """Write symbolic metadata demo Markdown report."""

    validate_symbolic_metadata_demo_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
