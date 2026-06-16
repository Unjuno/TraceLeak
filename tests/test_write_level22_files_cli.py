from scripts import write_level22_files as cli


def test_write_level22_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level22"
    monkeypatch.setattr("sys.argv", ["write_level22_files", "--out-dir", str(out_dir)])

    assert cli.main() == 0
    assert (out_dir / "level22-index.json").exists()
    assert (out_dir / "level22-index-report.md").exists()
