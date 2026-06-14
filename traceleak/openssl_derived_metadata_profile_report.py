"""Markdown report for Level 6 OpenSSL-derived metadata profile demos."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from traceleak.openssl_derived_metadata_profile_demo_chain import (
    validate_openssl_derived_metadata_profile_demo_summary,
)

OPENSSL_DERIVED_METADATA_PROFILE_REPORT_PHASE = "P100"


class OpenSSLDerivedMetadataProfileReportError(ValueError):
    """Raised when a Level 6 profile report is invalid."""


def render_openssl_derived_metadata_profile_report(summary: dict[str, Any]) -> str:
    """Render a Markdown report from a Level 6 profile demo summary."""

    validate_openssl_derived_metadata_profile_demo_summary(summary)
    lines = [
        "# OpenSSL-Derived Metadata Profile Report",
        "",
        f"- Report phase: `{OPENSSL_DERIVED_METADATA_PROFILE_REPORT_PHASE}`",
        f"- Demo phase: `{summary['phase']}`",
        f"- Mode: `{summary['mode']}`",
        f"- Target: `{summary['target']}`",
        f"- View: `{summary['view']}`",
        "",
        "## Profile status",
        "",
        f"- Profile format: `{summary['profile_format']}`",
        f"- Adapter input format: `{summary['adapter_input_format']}`",
        f"- Model-sequence format: `{summary['model_sequence_format']}`",
        f"- Record count: `{summary['record_count']}`",
        "",
        "## Safety boundary",
        "",
        f"- metadata_only: `{summary['flags']['metadata_only']}`",
        f"- payload_free: `{summary['flags']['payload_free']}`",
        f"- public_safe: `{summary['flags']['public_safe']}`",
        f"- payload_inspected: `{summary['flags']['payload_inspected']}`",
        f"- openssl_leakage_claim: `{summary['flags']['openssl_leakage_claim']}`",
        "",
        "## Label distribution",
        "",
    ]
    for label, count in sorted(summary["label_distribution"].items()):
        lines.append(f"- `{label}`: `{count}`")
    lines.extend(
        [
            "",
            "## Baseline metrics",
            "",
            f"- Majority accuracy: `{summary['baseline_summary']['majority_accuracy']}`",
            f"- Nearest-neighbor accuracy: `{summary['baseline_summary']['nearest_neighbor_accuracy']}`",
            "",
            "## NN metrics",
            "",
            f"- Model: `{summary['nn_summary']['model_name']}`",
            f"- Accuracy: `{summary['nn_summary']['accuracy']}`",
            f"- Attribution count: `{summary['nn_summary']['attribution_count']}`",
            "",
            "## Adapter bridge status",
            "",
            f"- Profile to adapter: `{summary['bridge_summary']['profile_to_adapter']}`",
            f"- Adapter to model-sequence: `{summary['bridge_summary']['adapter_to_model_sequence']}`",
            f"- Baseline generated: `{summary['bridge_summary']['baseline_generated']}`",
            f"- NN generated: `{summary['bridge_summary']['nn_generated']}`",
            "",
            "## Next-step guidance",
            "",
            f"- Next level: `{summary['next_level']['level']}`",
            f"- Next level name: `{summary['next_level']['name']}`",
            f"- Requires review: `{summary['next_level']['requires_review']}`",
            "",
            "## Notes",
            "",
            "This report summarizes metadata-only local profile demo output.",
            "It is not OpenSSL leakage evidence.",
            "It does not include OpenSSL source text, command text, build output, execution output, raw capture, private material, or runtime payloads.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    validate_openssl_derived_metadata_profile_report(markdown)
    return markdown


def validate_openssl_derived_metadata_profile_report(markdown: str) -> None:
    """Validate Level 6 profile report Markdown shape."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise OpenSSLDerivedMetadataProfileReportError("markdown must be a newline-terminated string")
    for text in [
        "# OpenSSL-Derived Metadata Profile Report",
        "## Profile status",
        "## Safety boundary",
        "## Label distribution",
        "## Baseline metrics",
        "## NN metrics",
        "## Adapter bridge status",
        "## Next-step guidance",
        "It is not OpenSSL leakage evidence.",
    ]:
        if text not in markdown:
            raise OpenSSLDerivedMetadataProfileReportError(f"missing markdown text: {text}")


def write_openssl_derived_metadata_profile_report(path: Path, markdown: str) -> None:
    """Write Level 6 profile report Markdown."""

    validate_openssl_derived_metadata_profile_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
