import json

import pytest

from traceleak.metadata_demo_markdown_summary import (
    REQUIRED_MARKDOWN_HEADINGS,
    MetadataDemoMarkdownSummaryError,
    render_metadata_demo_markdown_summary,
    render_metadata_demo_markdown_summary_from_artifacts,
    validate_metadata_demo_markdown_summary,
)
from traceleak.metadata_demo_token_ranking import build_metadata_demo_token_ranking
from traceleak.openssl_metadata_demo_chain import (
    build_openssl_metadata_demo_chain,
    write_openssl_metadata_demo_chain,
)


def test_metadata_demo_markdown_summary_renders_basic_sections(metadata_demo_artifacts) -> None:
    markdown = render_metadata_demo_markdown_summary(
        summary=metadata_demo_artifacts["demo_summary"],
        manifest=metadata_demo_artifacts["demo_manifest"],
    )

    assert "# Metadata Demo Summary" in markdown
    assert "## Status" in markdown
    assert "## Baseline" in markdown
    assert "## Neural model" in markdown
    assert metadata_demo_artifacts["demo_summary"]["sample_id"] in markdown


def test_metadata_demo_markdown_summary_headings_are_ordered(metadata_demo_artifacts) -> None:
    markdown = render_metadata_demo_markdown_summary(
        summary=metadata_demo_artifacts["demo_summary"],
        manifest=metadata_demo_artifacts["demo_manifest"],
    )

    previous = -1
    for heading in REQUIRED_MARKDOWN_HEADINGS:
        current = markdown.find(heading)
        assert current > previous
        previous = current
    assert markdown.endswith("\n")
    validate_metadata_demo_markdown_summary(markdown)


def test_metadata_demo_markdown_summary_renders_ranking_table(metadata_demo_artifacts) -> None:
    ranking = build_metadata_demo_token_ranking(
        demo_manifest=metadata_demo_artifacts["demo_manifest"],
        nn_result=metadata_demo_artifacts["nn_result"],
    )
    markdown = render_metadata_demo_markdown_summary(
        summary=metadata_demo_artifacts["demo_summary"],
        manifest=metadata_demo_artifacts["demo_manifest"],
        ranking=ranking,
    )

    assert "## Top ranked demo tokens" in markdown
    assert "| Rank | Token | Score |" in markdown


def test_metadata_demo_markdown_summary_from_artifacts_can_include_ranking(metadata_demo_artifacts) -> None:
    markdown = render_metadata_demo_markdown_summary_from_artifacts(
        metadata_demo_artifacts,
        include_ranking=True,
    )

    assert "# Metadata Demo Summary" in markdown
    assert "## Top ranked demo tokens" in markdown
    validate_metadata_demo_markdown_summary(markdown)


def test_metadata_demo_markdown_summary_from_written_chain_outputs(tmp_path) -> None:
    out_dir = tmp_path / "metadata_demo"
    artifacts = build_openssl_metadata_demo_chain(epochs=20)
    write_openssl_metadata_demo_chain(output_dir=out_dir, artifacts=artifacts)
    summary = json.loads((out_dir / "demo-summary.json").read_text(encoding="utf-8"))
    manifest = json.loads((out_dir / "demo-manifest.json").read_text(encoding="utf-8"))

    markdown = render_metadata_demo_markdown_summary(summary=summary, manifest=manifest)

    assert summary["sample_id"] in markdown
    assert str(summary["record_count"]) in markdown
    validate_metadata_demo_markdown_summary(markdown)


def test_metadata_demo_markdown_summary_rejects_manifest_mismatch(metadata_demo_artifacts) -> None:
    manifest = dict(metadata_demo_artifacts["demo_manifest"])
    manifest["sample_digest"] = "sha256:other"

    with pytest.raises(MetadataDemoMarkdownSummaryError, match="sample_digest"):
        render_metadata_demo_markdown_summary(
            summary=metadata_demo_artifacts["demo_summary"],
            manifest=manifest,
        )


def test_metadata_demo_markdown_summary_validator_rejects_missing_heading(metadata_demo_artifacts) -> None:
    markdown = render_metadata_demo_markdown_summary(
        summary=metadata_demo_artifacts["demo_summary"],
        manifest=metadata_demo_artifacts["demo_manifest"],
    ).replace("## Baseline", "## Other")

    with pytest.raises(MetadataDemoMarkdownSummaryError, match="missing heading"):
        validate_metadata_demo_markdown_summary(markdown)
