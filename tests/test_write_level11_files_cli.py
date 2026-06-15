from scripts import write_level11_files as cli


def test_write_level11_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level11"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level11_files",
            "--out-dir",
            str(out_dir),
            "--root-dir",
            str(tmp_path),
        ],
    )

    assert cli.main() == 0
    assert (out_dir / "level11-next-todo-proposal.json").exists()
    assert (out_dir / "level11-next-todo-proposal.md").exists()


def test_write_level11_files_cli_rejects_bad_reviewer(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level11"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level11_files",
            "--out-dir",
            str(out_dir),
            "--root-dir",
            str(tmp_path),
            "--reviewer",
            "",
        ],
    )

    assert cli.main() == 1
    assert not (out_dir / "level11-next-todo-proposal.json").exists()
