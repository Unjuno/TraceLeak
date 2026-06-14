import json

import pytest

from traceleak.local_report_bundle import (
    LOCAL_REPORT_BUNDLE_FORMAT,
    LocalReportBundleError,
    run_local_report_bundle,
    validate_local_report_bundle_summary,
)


def test_local_report_bundle_writes_all_report_surfaces(tmp_path) -> None:
    summary = run_local_report_bundle(root_dir=tmp_path, record_count=4, epochs=20)

    assert summary["format"] == LOCAL_REPORT_BUNDLE_FORMAT
    assert summary["phase"] == "P93"
    assert summary["next_level"]["level"] == 6
    assert summary["next_level"]["ready_after_local_validation"] is True
    assert summary["dashboard_missing_count"] == 0
    assert (tmp_path / "openssl_metadata_demo" / "demo-summary.json").exists()
    assert (tmp_path / "openssl_metadata_demo" / "demo-summary.md").exists()
    assert (tmp_path / "openssl_metadata_demo" / "demo-metrics.json").exists()
    assert (tmp_path / "openssl_metadata_demo" / "artifact-index.json").exists()
    assert (tmp_path / "symbolic_metadata_demo" / "symbolic-demo-summary.json").exists()
    assert (tmp_path / "symbolic_metadata_demo" / "symbolic-demo-report.md").exists()
    assert (tmp_path / "demo-summary-comparison.json").exists()
    assert (tmp_path / "demo-summary-comparison.md").exists()
    assert (tmp_path / "local-demo-dashboard.json").exists()
    assert (tmp_path / "local-demo-dashboard.md").exists()
    assert (tmp_path / "local-report-bundle-summary.json").exists()
    validate_local_report_bundle_summary(summary)


def test_local_report_bundle_summary_file_matches_returned_summary(tmp_path) -> None:
    summary = run_local_report_bundle(root_dir=tmp_path, record_count=4, epochs=20)

    loaded = json.loads((tmp_path / "local-report-bundle-summary.json").read_text(encoding="utf-8"))

    assert loaded == summary
    assert loaded["outputs"]["dashboard"].endswith("local-demo-dashboard.json")


def test_local_report_bundle_rejects_bad_record_count(tmp_path) -> None:
    with pytest.raises(LocalReportBundleError, match="record_count"):
        run_local_report_bundle(root_dir=tmp_path, record_count=3, epochs=20)

    assert not (tmp_path / "local-report-bundle-summary.json").exists()


def test_local_report_bundle_rejects_bad_epochs(tmp_path) -> None:
    with pytest.raises(LocalReportBundleError, match="epochs"):
        run_local_report_bundle(root_dir=tmp_path, record_count=4, epochs=0)

    assert not (tmp_path / "local-report-bundle-summary.json").exists()
