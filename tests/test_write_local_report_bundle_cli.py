from scripts import write_local_report_bundle as cli


def test_write_local_report_bundle_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    root_dir = tmp_path / "reports" / "local"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_local_report_bundle",
            "--root-dir",
            str(root_dir),
            "--record-count",
            "4",
            "--epochs",
            "20",
        ],
    )

    assert cli.main() == 0
    assert (root_dir / "openssl_metadata_demo" / "demo-summary.json").exists()
    assert (root_dir / "symbolic_metadata_demo" / "symbolic-demo-summary.json").exists()
    assert (root_dir / "demo-summary-comparison.json").exists()
    assert (root_dir / "local-demo-dashboard.json").exists()
    assert (root_dir / "local-report-bundle-summary.json").exists()


def test_write_local_report_bundle_cli_rejects_bad_epochs(tmp_path, monkeypatch) -> None:
    root_dir = tmp_path / "reports" / "local"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_local_report_bundle",
            "--root-dir",
            str(root_dir),
            "--epochs",
            "0",
        ],
    )

    assert cli.main() == 1
    assert not (root_dir / "local-report-bundle-summary.json").exists()
