from scripts import write_level24_files as cli


def test_write_level24_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level24"
    monkeypatch.setattr("sys.argv", ["write_level24_files", "--out-dir", str(out_dir)])

    assert cli.main() == 0
    assert (out_dir / "level24-index.json").exists()
    assert (out_dir / "level24-index-report.md").exists()
