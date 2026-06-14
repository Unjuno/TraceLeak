from scripts import write_level6_artifacts as cli


def test_write_level6_artifacts_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "level6"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level6_artifacts",
            "--out-dir",
            str(out_dir),
            "--epochs",
            "20",
            "--write-report",
        ],
    )

    assert cli.main() == 0
    assert (out_dir / "profile-input.json").exists()
    assert (out_dir / "adapter-input.json").exists()
    assert (out_dir / "profile-model-sequence.json").exists()
    assert (out_dir / "profile-baseline-result.json").exists()
    assert (out_dir / "profile-nn-result.json").exists()
    assert (out_dir / "profile-demo-summary.json").exists()
    assert (out_dir / "profile-demo-report.md").exists()


def test_write_level6_artifacts_cli_rejects_bad_epochs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "level6"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level6_artifacts",
            "--out-dir",
            str(out_dir),
            "--epochs",
            "0",
        ],
    )

    assert cli.main() == 1
    assert not (out_dir / "profile-demo-summary.json").exists()
