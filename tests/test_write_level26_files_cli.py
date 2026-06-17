from scripts import write_level26_files as cli


def test_write_level26_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level26"
    monkeypatch.setattr("sys.argv", ["write_level26_files", "--out-dir", str(out_dir)])

    assert cli.main() == 0
    assert (out_dir / "level26-index.json").exists()
    assert (out_dir / "level26-index-report.md").exists()
