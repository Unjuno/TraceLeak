import json

from scripts import write_level16_files as cli


def test_write_level16_files_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level16"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level16_files",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert cli.main() == 0
    assert json.loads((out_dir / "level16-review.json").read_text(encoding="utf-8"))["format"] == cli.LEVEL16_LOCAL_REVIEW_FORMAT
    assert (out_dir / "level16-review-report.md").read_text(encoding="utf-8").startswith("# Level 16 Local Review")


def test_write_level16_files_cli_rejects_bad_reviewer(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "reports" / "local" / "level16"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level16_files",
            "--out-dir",
            str(out_dir),
            "--reviewer",
            "",
        ],
    )

    assert cli.main() == 1
    assert not (out_dir / "level16-review.json").exists()
