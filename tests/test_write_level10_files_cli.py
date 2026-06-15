from scripts import write_level10_files as cli


def test_write_level10_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level10"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level10_files",
            "--out-dir",
            str(out_dir),
            "--root-dir",
            str(tmp_path),
        ],
    )

    assert cli.main() == 0
    assert (out_dir / "level10-review-packet.json").exists()
    assert (out_dir / "level10-review-packet.md").exists()


def test_write_level10_files_cli_rejects_bad_reviewer(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level10"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level10_files",
            "--out-dir",
            str(out_dir),
            "--root-dir",
            str(tmp_path),
            "--reviewer",
            "",
        ],
    )

    assert cli.main() == 1
    assert not (out_dir / "level10-review-packet.json").exists()
