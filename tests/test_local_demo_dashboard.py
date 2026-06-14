import json

import pytest

from traceleak.demo_summary_comparison import (
    build_demo_summary_comparison,
    render_demo_summary_comparison_markdown,
    write_demo_summary_comparison_json,
    write_demo_summary_comparison_markdown,
)
from traceleak.local_demo_dashboard import (
    LOCAL_DEMO_DASHBOARD_FORMAT,
    LocalDemoDashboardError,
    build_local_demo_dashboard,
    render_local_demo_dashboard_markdown,
    validate_local_demo_dashboard,
    validate_local_demo_dashboard_markdown,
    write_local_demo_dashboard_json,
    write_local_demo_dashboard_markdown,
)
from traceleak.metadata_demo_artifact_index import build_metadata_demo_artifact_index
from traceleak.metadata_demo_artifact_index import render_metadata_demo_artifact_index_markdown
from traceleak.metadata_demo_artifact_index import write_metadata_demo_artifact_index_json
from traceleak.metadata_demo_artifact_index import write_metadata_demo_artifact_index_markdown
from traceleak.metadata_demo_markdown_summary import (
    render_metadata_demo_markdown_summary_from_artifacts,
    write_metadata_demo_markdown_summary,
)
from traceleak.metadata_demo_metrics import (
    build_metadata_demo_metrics_from_artifacts,
    write_metadata_demo_metrics_csv,
    write_metadata_demo_metrics_json,
)
from traceleak.openssl_metadata_demo_chain import (
    build_openssl_metadata_demo_chain,
    write_openssl_metadata_demo_chain,
)
from traceleak.symbolic_metadata_demo_chain import (
    build_symbolic_metadata_demo_chain,
    write_symbolic_metadata_demo_chain,
)
from traceleak.symbolic_metadata_demo_report import (
    render_symbolic_metadata_demo_report,
    write_symbolic_metadata_demo_report,
)


def write_local_demo_outputs(root_dir):
    metadata_dir = root_dir / "openssl_metadata_demo"
    symbolic_dir = root_dir / "symbolic_metadata_demo"
    metadata_artifacts = build_openssl_metadata_demo_chain(epochs=20)
    symbolic_artifacts = build_symbolic_metadata_demo_chain(epochs=20)
    write_openssl_metadata_demo_chain(output_dir=metadata_dir, artifacts=metadata_artifacts)
    write_metadata_demo_markdown_summary(
        metadata_dir / "demo-summary.md",
        render_metadata_demo_markdown_summary_from_artifacts(metadata_artifacts, include_ranking=True),
    )
    metrics = build_metadata_demo_metrics_from_artifacts(metadata_artifacts)
    write_metadata_demo_metrics_json(metadata_dir / "demo-metrics.json", metrics)
    write_metadata_demo_metrics_csv(metadata_dir / "demo-metrics.csv", metrics)
    index = build_metadata_demo_artifact_index(output_dir=metadata_dir)
    write_metadata_demo_artifact_index_json(metadata_dir / "artifact-index.json", index)
    write_metadata_demo_artifact_index_markdown(
        metadata_dir / "artifact-index.md",
        render_metadata_demo_artifact_index_markdown(index),
    )
    write_symbolic_metadata_demo_chain(output_dir=symbolic_dir, artifacts=symbolic_artifacts)
    write_symbolic_metadata_demo_report(
        symbolic_dir / "symbolic-demo-report.md",
        render_symbolic_metadata_demo_report(symbolic_artifacts["demo_summary"]),
    )
    comparison = build_demo_summary_comparison(
        metadata_summary=metadata_artifacts["demo_summary"],
        symbolic_summary=symbolic_artifacts["demo_summary"],
    )
    write_demo_summary_comparison_json(root_dir / "demo-summary-comparison.json", comparison)
    write_demo_summary_comparison_markdown(
        root_dir / "demo-summary-comparison.md",
        render_demo_summary_comparison_markdown(comparison),
    )


def test_local_demo_dashboard_builds_from_generated_outputs(tmp_path) -> None:
    write_local_demo_outputs(tmp_path)

    dashboard = build_local_demo_dashboard(root_dir=tmp_path)

    assert dashboard["format"] == LOCAL_DEMO_DASHBOARD_FORMAT
    assert dashboard["phase"] == "P90"
    assert dashboard["present_count"] == dashboard["entry_count"]
    assert dashboard["missing_count"] == 0
    assert dashboard["payload_inspected"] is False
    validate_local_demo_dashboard(dashboard)


def test_local_demo_dashboard_marks_missing_outputs(tmp_path) -> None:
    dashboard = build_local_demo_dashboard(root_dir=tmp_path)

    assert dashboard["present_count"] == 0
    assert dashboard["missing_count"] == dashboard["entry_count"]


def test_local_demo_dashboard_renders_markdown(tmp_path) -> None:
    write_local_demo_outputs(tmp_path)
    dashboard = build_local_demo_dashboard(root_dir=tmp_path)

    markdown = render_local_demo_dashboard_markdown(dashboard)

    assert "# Local Demo Dashboard" in markdown
    assert "traceleak-compare-demo-summaries" in markdown
    assert "not OpenSSL leakage evidence" in markdown
    validate_local_demo_dashboard_markdown(markdown)


def test_local_demo_dashboard_writes_json_and_markdown(tmp_path) -> None:
    write_local_demo_outputs(tmp_path)
    dashboard = build_local_demo_dashboard(root_dir=tmp_path)
    json_path = tmp_path / "dashboard.json"
    markdown_path = tmp_path / "dashboard.md"

    write_local_demo_dashboard_json(json_path, dashboard)
    write_local_demo_dashboard_markdown(markdown_path, render_local_demo_dashboard_markdown(dashboard))

    assert json.loads(json_path.read_text(encoding="utf-8"))["format"] == LOCAL_DEMO_DASHBOARD_FORMAT
    assert markdown_path.read_text(encoding="utf-8").startswith("# Local Demo Dashboard")


def test_local_demo_dashboard_rejects_parent_traversal(tmp_path) -> None:
    with pytest.raises(LocalDemoDashboardError, match="plain relative path"):
        build_local_demo_dashboard(
            root_dir=tmp_path,
            expected_files={"bad": {"path": "../bad.json", "role": "bad"}},
        )
