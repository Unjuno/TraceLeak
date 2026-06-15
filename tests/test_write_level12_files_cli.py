from scripts import write_level12_files as cli


def test_write_level12_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level12"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level12_files",
            "--out-dir",
            str(out_dir),
            "--root-dir",
            str(tmp_path),
        ],
    )

    assert cli.main() == 0
    assert (out_dir / "level12-review-checkpoint.json").exists()
    assert (out_dir / "level12-review-checkpoint.md").exists()


def test_write_level12_files_cli_rejects_bad_reviewer(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level12"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level12_files",
            "--out-dir",
            str(out_dir),
            "--root-dir",
            str(tmp_path),
            "--reviewer",
            "",
        ],
    )

    assert cli.main() == 1
    assert not (out_dir / "level12-review-checkpoint.json").exists()
