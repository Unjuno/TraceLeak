from scripts import write_level15_files as cli


def test_write_level15_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level15"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level15_files",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert cli.main() == 0
    assert (out_dir / "level15-validation-rollup.json").exists()
    assert (out_dir / "level15-validation-rollup-report.md").exists()


def test_write_level15_files_cli_rejects_bad_reviewer(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level15"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level15_files",
            "--out-dir",
            str(out_dir),
            "--reviewer",
            "",
        ],
    )

    assert cli.main() == 1
    assert not (out_dir / "level15-validation-rollup.json").exists()
