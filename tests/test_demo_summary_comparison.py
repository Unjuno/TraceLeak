import json

import pytest

from traceleak.demo_summary_comparison import (
    DEMO_SUMMARY_COMPARISON_FORMAT,
    DemoSummaryComparisonError,
    build_demo_summary_comparison,
    render_demo_summary_comparison_markdown,
    validate_demo_summary_comparison,
    validate_demo_summary_comparison_markdown,
    write_demo_summary_comparison_json,
    write_demo_summary_comparison_markdown,
)
from traceleak.openssl_metadata_demo_chain import build_openssl_metadata_demo_chain
from traceleak.symbolic_metadata_demo_chain import build_symbolic_metadata_demo_chain


def summaries() -> tuple[dict, dict]:
    metadata = build_openssl_metadata_demo_chain(epochs=20)["demo_summary"]
    symbolic = build_symbolic_metadata_demo_chain(epochs=20)["demo_summary"]
    return metadata, symbolic


def test_demo_summary_comparison_builds_from_demo_summaries() -> None:
    metadata, symbolic = summaries()

    comparison = build_demo_summary_comparison(
        metadata_summary=metadata,
        symbolic_summary=symbolic,
    )

    assert comparison["format"] == DEMO_SUMMARY_COMPARISON_FORMAT
    assert comparison["phase"] == "P87"
    assert comparison["flags"]["metadata_only"] is True
    assert comparison["flags"]["openssl_leakage_claim"] is False
    assert comparison["left"]["format"] == metadata["format"]
    assert comparison["right"]["format"] == symbolic["format"]
    assert "nn_accuracy" in comparison["deltas"]
    validate_demo_summary_comparison(comparison)


def test_demo_summary_comparison_renders_markdown() -> None:
    metadata, symbolic = summaries()
    comparison = build_demo_summary_comparison(
        metadata_summary=metadata,
        symbolic_summary=symbolic,
    )

    markdown = render_demo_summary_comparison_markdown(comparison)

    assert "# Demo Summary Comparison" in markdown
    assert "| Metric | Metadata demo | Symbolic demo | Delta |" in markdown
    assert "## Safety flags" in markdown
    assert "not OpenSSL leakage evidence" in markdown
    validate_demo_summary_comparison_markdown(markdown)


def test_demo_summary_comparison_writes_json_and_markdown(tmp_path) -> None:
    metadata, symbolic = summaries()
    comparison = build_demo_summary_comparison(
        metadata_summary=metadata,
        symbolic_summary=symbolic,
    )
    json_path = tmp_path / "demo-summary-comparison.json"
    markdown_path = tmp_path / "demo-summary-comparison.md"

    write_demo_summary_comparison_json(json_path, comparison)
    write_demo_summary_comparison_markdown(
        markdown_path,
        render_demo_summary_comparison_markdown(comparison),
    )

    assert json.loads(json_path.read_text(encoding="utf-8"))["format"] == DEMO_SUMMARY_COMPARISON_FORMAT
    assert markdown_path.read_text(encoding="utf-8").startswith("# Demo Summary Comparison")


def test_demo_summary_comparison_rejects_wrong_metadata_format() -> None:
    metadata, symbolic = summaries()
    metadata = dict(metadata)
    metadata["format"] = "wrong"

    with pytest.raises(DemoSummaryComparisonError, match="metadata_summary.format"):
        build_demo_summary_comparison(metadata_summary=metadata, symbolic_summary=symbolic)


def test_demo_summary_comparison_rejects_non_metadata_only_flag() -> None:
    metadata, symbolic = summaries()
    symbolic = dict(symbolic)
    symbolic["flags"] = dict(symbolic["flags"])
    symbolic["flags"]["metadata_only"] = False

    with pytest.raises(DemoSummaryComparisonError, match="metadata_only"):
        build_demo_summary_comparison(metadata_summary=metadata, symbolic_summary=symbolic)
