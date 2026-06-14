import json

from scripts import run_symbolic_metadata_demo_chain as cli


def test_run_symbolic_metadata_demo_chain_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "symbolic_metadata_demo"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_symbolic_metadata_demo_chain",
            "--out-dir",
            str(out_dir),
            "--epochs",
            "20",
        ],
    )

    assert cli.main() == 0
    expected = [
        "symbolic-metadata-input.json",
        "runtime-gate.json",
        "symbolic-model-sequence.json",
        "symbolic-baseline-result.json",
        "symbolic-nn-result.json",
        "symbolic-demo-summary.json",
    ]
    for name in expected:
        assert (out_dir / name).exists(), name
    summary = json.loads((out_dir / "symbolic-demo-summary.json").read_text(encoding="utf-8"))
    assert summary["format"] == "traceleak.symbolic_metadata_demo_chain.v1"
    assert summary["phase"] == "P84"


def test_run_symbolic_metadata_demo_chain_cli_writes_report(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "symbolic_metadata_demo"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_symbolic_metadata_demo_chain",
            "--out-dir",
            str(out_dir),
            "--epochs",
            "20",
            "--write-report",
        ],
    )

    assert cli.main() == 0
    report = (out_dir / "symbolic-demo-report.md").read_text(encoding="utf-8")
    assert "# Symbolic Metadata Demo Report" in report
    assert "## Neural model" in report


def test_run_symbolic_metadata_demo_chain_cli_rejects_bad_epochs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "symbolic_metadata_demo"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_symbolic_metadata_demo_chain",
            "--out-dir",
            str(out_dir),
            "--epochs",
            "0",
        ],
    )

    assert cli.main() == 1
    assert not (out_dir / "symbolic-demo-summary.json").exists()
