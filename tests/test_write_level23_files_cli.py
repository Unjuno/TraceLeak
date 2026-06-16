from scripts import write_level23_files as cli


def test_write_level23_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level23"
    monkeypatch.setattr("sys.argv", ["write_level23_files", "--out-dir", str(out_dir)])

    assert cli.main() == 0
    assert (out_dir / "level23-index.json").exists()
    assert (out_dir / "level23-index-report.md").exists()
