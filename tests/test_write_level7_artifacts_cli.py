from scripts import write_level7_artifacts as cli


def test_write_level7_artifacts_cli_writes_gate_only_by_default(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "level7"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level7_artifacts",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert cli.main() == 0
    assert (out_dir / "level7-review-gate.json").exists()
    assert not (out_dir / "level7-planning-contract.json").exists()


def test_write_level7_artifacts_cli_writes_planning_artifacts_when_approved(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "level7"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level7_artifacts",
            "--out-dir",
            str(out_dir),
            "--approve-planning-only",
        ],
    )

    assert cli.main() == 0
    assert (out_dir / "level7-review-gate.json").exists()
    assert (out_dir / "level7-planning-contract.json").exists()
    assert (out_dir / "level7-artifact-boundary-plan.json").exists()
    assert (out_dir / "level7-review-checklist.json").exists()
    assert (out_dir / "level7-readiness-report.md").exists()


def test_write_level7_artifacts_cli_rejects_bad_reviewer(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "level7"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_level7_artifacts",
            "--out-dir",
            str(out_dir),
            "--reviewer",
            "",
            "--approve-planning-only",
        ],
    )

    assert cli.main() == 1
