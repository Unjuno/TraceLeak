"""Markdown summary renderer for metadata demo outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

REQUIRED_MARKDOWN_HEADINGS = [
    "# Metadata Demo Summary",
    "## Status",
    "## Safety flags",
    "## Baseline",
    "## Neural model",
    "## Manifest binding",
    "## Notes",
]


class MetadataDemoMarkdownSummaryError(ValueError):
    """Raised when metadata demo summary inputs are invalid."""


def render_metadata_demo_markdown_summary(
    *,
    summary: dict[str, Any],
    manifest: dict[str, Any],
    ranking: dict[str, Any] | None = None,
) -> str:
    """Render a compact Markdown summary from metadata demo outputs."""

    _require_summary(summary)
    _require_manifest(manifest, summary=summary)
    if ranking is not None:
        _require_ranking(ranking, summary=summary)
    lines = [
        "# Metadata Demo Summary",
        "",
        "## Status",
        "",
        f"- Phase: `{summary['phase']}`",
        f"- Sample ID: `{summary['sample_id']}`",
        f"- Record count: `{summary['record_count']}`",
        f"- Label name: `{summary['label_name']}`",
        "- Scope: metadata-only public demo",
        "",
        "## Safety flags",
        "",
        f"- metadata_only: `{summary['flags']['metadata_only']}`",
        f"- public_safe: `{summary['flags']['public_safe']}`",
        f"- demo claim only: `{not summary['flags']['openssl_leakage_claim']}`",
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
        "## Manifest binding",
        "",
        f"- Manifest phase: `{manifest['phase']}`",
        f"- Sample digest: `{manifest['sample_digest']}`",
        f"- Source pin digest: `{manifest['source_pin_digest']}`",
    ]
    if ranking is not None:
        lines.extend(
            [
                "",
                "## Top ranked demo tokens",
                "",
                "| Rank | Token | Score |",
                "|---:|---|---:|",
            ]
        )
        for row in ranking.get("ranked_tokens", [])[:5]:
            lines.append(f"| {row['rank']} | `{row['group_id']}` | `{row['score']}` |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This Markdown file summarizes metadata-demo outputs only.",
            "It is intended for local inspection and repository smoke checks.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    validate_metadata_demo_markdown_summary(markdown)
    return markdown


def render_metadata_demo_markdown_summary_from_artifacts(
    artifacts: dict[str, Any],
    *,
    include_ranking: bool = False,
) -> str:
    """Render Markdown directly from metadata demo chain artifacts."""

    summary = _dict(artifacts.get("demo_summary"), "artifacts.demo_summary")
    manifest = _dict(artifacts.get("demo_manifest"), "artifacts.demo_manifest")
    ranking = None
    if include_ranking:
        from traceleak.metadata_demo_token_ranking import build_metadata_demo_token_ranking

        ranking = build_metadata_demo_token_ranking(
            demo_manifest=manifest,
            nn_result=_dict(artifacts.get("nn_result"), "artifacts.nn_result"),
        )
    return render_metadata_demo_markdown_summary(
        summary=summary,
        manifest=manifest,
        ranking=ranking,
    )


def validate_metadata_demo_markdown_summary(markdown: str) -> None:
    """Validate the required Markdown summary shape."""

    if not isinstance(markdown, str) or not markdown:
        raise MetadataDemoMarkdownSummaryError("markdown must be a non-empty string")
    if not markdown.endswith("\n"):
        raise MetadataDemoMarkdownSummaryError("markdown must end with a newline")
    position = -1
    for heading in REQUIRED_MARKDOWN_HEADINGS:
        current = markdown.find(heading)
        if current < 0:
            raise MetadataDemoMarkdownSummaryError(f"missing heading: {heading}")
        if current <= position:
            raise MetadataDemoMarkdownSummaryError(f"heading out of order: {heading}")
        position = current


def write_metadata_demo_markdown_summary(path: Path, markdown: str) -> None:
    """Write a Markdown summary."""

    validate_metadata_demo_markdown_summary(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _require_summary(summary: dict[str, Any]) -> None:
    _eq(
        summary.get("format"),
        "traceleak.openssl_model_sequence_metadata_sample_demo_result.v1",
        "summary.format",
    )
    _eq(summary.get("phase"), "P24", "summary.phase")
    for field in ["sample_id", "sample_digest", "source_pin_digest", "label_name"]:
        _non_empty(summary.get(field), f"summary.{field}")
    if not isinstance(summary.get("record_count"), int) or summary["record_count"] <= 0:
        raise MetadataDemoMarkdownSummaryError("summary.record_count must be positive")
    flags = _dict(summary.get("flags"), "summary.flags")
    for flag in ["metadata_only", "public_safe", "baseline_result_generated", "model_result_generated"]:
        _eq(flags.get(flag), True, f"summary.flags.{flag}")
    _eq(flags.get("openssl_leakage_claim"), False, "summary.flags.openssl_leakage_claim")
    _dict(summary.get("baseline_summary"), "summary.baseline_summary")
    _dict(summary.get("nn_summary"), "summary.nn_summary")


def _require_manifest(manifest: dict[str, Any], *, summary: dict[str, Any]) -> None:
    _eq(manifest.get("format"), "traceleak.openssl_model_sequence_metadata_demo_manifest.v1", "manifest.format")
    _eq(manifest.get("phase"), "P26", "manifest.phase")
    for field in ["sample_id", "sample_digest", "source_pin_digest"]:
        _eq(manifest.get(field), summary[field], f"manifest.{field}")
    public_statement = _dict(manifest.get("public_statement"), "manifest.public_statement")
    _eq(public_statement.get("metadata_only"), True, "manifest.public_statement.metadata_only")
    _eq(public_statement.get("public_safe"), True, "manifest.public_statement.public_safe")


def _require_ranking(ranking: dict[str, Any], *, summary: dict[str, Any]) -> None:
    _eq(ranking.get("format"), "traceleak.metadata_demo_token_ranking.v1", "ranking.format")
    _eq(ranking.get("phase"), "P30", "ranking.phase")
    _eq(ranking.get("sample_digest"), summary["sample_digest"], "ranking.sample_digest")
    rows = ranking.get("ranked_tokens")
    if not isinstance(rows, list):
        raise MetadataDemoMarkdownSummaryError("ranking.ranked_tokens must be a list")


def _dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MetadataDemoMarkdownSummaryError(f"{name} must be an object")
    return value


def _non_empty(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise MetadataDemoMarkdownSummaryError(f"{name} must be a non-empty string")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise MetadataDemoMarkdownSummaryError(f"{name} must be {expected!r}")
