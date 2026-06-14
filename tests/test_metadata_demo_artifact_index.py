import json

import pytest

from traceleak.metadata_demo_artifact_index import (
    METADATA_DEMO_ARTIFACT_INDEX_FORMAT,
    MetadataDemoArtifactIndexError,
    build_metadata_demo_artifact_index,
    render_metadata_demo_artifact_index_markdown,
    validate_metadata_demo_artifact_index,
    validate_metadata_demo_artifact_index_markdown,
    write_metadata_demo_artifact_index_json,
    write_metadata_demo_artifact_index_markdown,
)
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


def write_demo_outputs(tmp_path):
    out_dir = tmp_path / "metadata_demo"
    artifacts = build_openssl_metadata_demo_chain(epochs=20)
    write_openssl_metadata_demo_chain(output_dir=out_dir, artifacts=artifacts)
    markdown = render_metadata_demo_markdown_summary_from_artifacts(artifacts, include_ranking=True)
    write_metadata_demo_markdown_summary(out_dir / "demo-summary.md", markdown)
    metrics = build_metadata_demo_metrics_from_artifacts(artifacts)
    write_metadata_demo_metrics_json(out_dir / "demo-metrics.json", metrics)
    write_metadata_demo_metrics_csv(out_dir / "demo-metrics.csv", metrics)
    return out_dir


def test_metadata_demo_artifact_index_lists_expected_local_outputs(tmp_path) -> None:
    out_dir = write_demo_outputs(tmp_path)

    index = build_metadata_demo_artifact_index(output_dir=out_dir)

    assert index["format"] == METADATA_DEMO_ARTIFACT_INDEX_FORMAT
    assert index["phase"] == "P76"
    assert index["present_count"] == index["file_count"]
    assert index["missing_count"] == 0
    assert index["payload_inspected"] is False
    assert {item["filename"] for item in index["files"]} >= {"demo-summary.md", "demo-metrics.json", "demo-metrics.csv"}
    validate_metadata_demo_artifact_index(index)


def test_metadata_demo_artifact_index_marks_missing_optional_outputs(tmp_path) -> None:
    out_dir = tmp_path / "metadata_demo"
    artifacts = build_openssl_metadata_demo_chain(epochs=20)
    write_openssl_metadata_demo_chain(output_dir=out_dir, artifacts=artifacts)

    index = build_metadata_demo_artifact_index(output_dir=out_dir)

    missing = {item["filename"] for item in index["files"] if not item["exists"]}
    assert "demo-summary.md" in missing
    assert "demo-metrics.json" in missing
    assert "demo-metrics.csv" in missing
    assert index["missing_count"] == 3


def test_metadata_demo_artifact_index_renders_markdown(tmp_path) -> None:
    index = build_metadata_demo_artifact_index(output_dir=write_demo_outputs(tmp_path))

    markdown = render_metadata_demo_artifact_index_markdown(index)

    assert "# Metadata Demo Artifact Index" in markdown
    assert "| File | Role | Status | Size bytes |" in markdown
    assert "`demo-summary.md`" in markdown
    validate_metadata_demo_artifact_index_markdown(markdown)


def test_metadata_demo_artifact_index_writes_json_and_markdown(tmp_path) -> None:
    index = build_metadata_demo_artifact_index(output_dir=write_demo_outputs(tmp_path))
    json_path = tmp_path / "index.json"
    markdown_path = tmp_path / "index.md"

    write_metadata_demo_artifact_index_json(json_path, index)
    write_metadata_demo_artifact_index_markdown(markdown_path, render_metadata_demo_artifact_index_markdown(index))

    assert json.loads(json_path.read_text(encoding="utf-8"))["format"] == METADATA_DEMO_ARTIFACT_INDEX_FORMAT
    assert markdown_path.read_text(encoding="utf-8").startswith("# Metadata Demo Artifact Index")


def test_metadata_demo_artifact_index_rejects_unsafe_filename(tmp_path) -> None:
    with pytest.raises(MetadataDemoArtifactIndexError, match="plain relative"):
        build_metadata_demo_artifact_index(
            output_dir=tmp_path,
            expected_files={"../bad.json": "bad"},
        )
