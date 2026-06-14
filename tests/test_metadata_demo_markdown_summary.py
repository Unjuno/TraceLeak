import pytest

from traceleak.metadata_demo_markdown_summary import (
    MetadataDemoMarkdownSummaryError,
    render_metadata_demo_markdown_summary,
)
from traceleak.metadata_demo_token_ranking import build_metadata_demo_token_ranking


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


def test_metadata_demo_markdown_summary_rejects_manifest_mismatch(metadata_demo_artifacts) -> None:
    manifest = dict(metadata_demo_artifacts["demo_manifest"])
    manifest["sample_digest"] = "sha256:other"

    with pytest.raises(MetadataDemoMarkdownSummaryError, match="sample_digest"):
        render_metadata_demo_markdown_summary(
            summary=metadata_demo_artifacts["demo_summary"],
            manifest=manifest,
        )
