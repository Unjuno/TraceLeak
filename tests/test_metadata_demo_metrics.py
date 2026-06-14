import csv
import json

import pytest

from traceleak.metadata_demo_metrics import (
    CSV_COLUMNS,
    METADATA_DEMO_METRICS_FORMAT,
    MetadataDemoMetricsError,
    build_metadata_demo_metrics,
    build_metadata_demo_metrics_from_artifacts,
    render_metadata_demo_metrics_csv,
    validate_metadata_demo_metrics,
    write_metadata_demo_metrics_csv,
    write_metadata_demo_metrics_json,
)


def test_metadata_demo_metrics_builds_compact_object(metadata_demo_artifacts) -> None:
    metrics = build_metadata_demo_metrics(
        summary=metadata_demo_artifacts["demo_summary"],
        manifest=metadata_demo_artifacts["demo_manifest"],
    )

    assert metrics["format"] == METADATA_DEMO_METRICS_FORMAT
    assert metrics["phase"] == "P66"
    assert metrics["record_count"] == metadata_demo_artifacts["demo_summary"]["record_count"]
    assert metrics["label_count"] == len(metadata_demo_artifacts["demo_summary"]["label_distribution"])
    assert metrics["metadata_only"] is True
    assert metrics["public_safe"] is True
    assert metrics["demo_claim_only"] is True
    validate_metadata_demo_metrics(metrics)


def test_metadata_demo_metrics_builds_from_artifacts(metadata_demo_artifacts) -> None:
    metrics = build_metadata_demo_metrics_from_artifacts(metadata_demo_artifacts)

    assert metrics["sample_id"] == metadata_demo_artifacts["demo_summary"]["sample_id"]
    assert metrics["sample_digest"] == metadata_demo_artifacts["demo_manifest"]["sample_digest"]


def test_metadata_demo_metrics_csv_has_stable_columns(metadata_demo_artifacts) -> None:
    metrics = build_metadata_demo_metrics_from_artifacts(metadata_demo_artifacts)
    text = render_metadata_demo_metrics_csv(metrics)
    rows = list(csv.DictReader(text.splitlines()))

    assert text.endswith("\n")
    assert rows
    assert list(rows[0]) == CSV_COLUMNS
    assert rows[0]["format"] == METADATA_DEMO_METRICS_FORMAT
    assert rows[0]["sample_id"] == metrics["sample_id"]


def test_metadata_demo_metrics_writes_json_and_csv(tmp_path, metadata_demo_artifacts) -> None:
    metrics = build_metadata_demo_metrics_from_artifacts(metadata_demo_artifacts)
    json_path = tmp_path / "demo-metrics.json"
    csv_path = tmp_path / "demo-metrics.csv"

    write_metadata_demo_metrics_json(json_path, metrics)
    write_metadata_demo_metrics_csv(csv_path, metrics)

    assert json.loads(json_path.read_text(encoding="utf-8"))["format"] == METADATA_DEMO_METRICS_FORMAT
    assert csv_path.read_text(encoding="utf-8").startswith("format,phase,sample_id")


def test_metadata_demo_metrics_rejects_manifest_mismatch(metadata_demo_artifacts) -> None:
    manifest = dict(metadata_demo_artifacts["demo_manifest"])
    manifest["sample_digest"] = "sha256:other"

    with pytest.raises(MetadataDemoMetricsError, match="sample_digest"):
        build_metadata_demo_metrics(
            summary=metadata_demo_artifacts["demo_summary"],
            manifest=manifest,
        )


def test_metadata_demo_metrics_rejects_bad_score(metadata_demo_artifacts) -> None:
    metrics = build_metadata_demo_metrics_from_artifacts(metadata_demo_artifacts)
    metrics["nn_accuracy"] = 2.0

    with pytest.raises(MetadataDemoMetricsError, match="nn_accuracy"):
        validate_metadata_demo_metrics(metrics)
