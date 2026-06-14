import csv
import json

from scripts import run_openssl_metadata_demo_chain as cli


def test_run_openssl_metadata_demo_chain_cli_writes_artifacts(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "openssl_metadata_demo"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_openssl_metadata_demo_chain",
            "--out-dir",
            str(out_dir),
            "--record-count",
            "4",
            "--epochs",
            "20",
        ],
    )

    assert cli.main() == 0
    expected = [
        "sample-contract.json",
        "sample-manifest.json",
        "approval-record.json",
        "approval-gate.json",
        "request-contract.json",
        "output-contract.json",
        "output-manifest.json",
        "metadata-sample.json",
        "model-preflight.json",
        "demo-summary.json",
        "baseline-result.json",
        "nn-result.json",
        "demo-manifest.json",
    ]
    for name in expected:
        assert (out_dir / name).exists(), name
    summary = json.loads((out_dir / "demo-summary.json").read_text(encoding="utf-8"))
    assert summary["phase"] == "P24"
    assert summary["flags"]["metadata_only"] is True


def test_run_openssl_metadata_demo_chain_cli_writes_markdown_summary(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "openssl_metadata_demo"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_openssl_metadata_demo_chain",
            "--out-dir",
            str(out_dir),
            "--record-count",
            "4",
            "--epochs",
            "20",
            "--write-markdown-summary",
            "--include-ranking",
        ],
    )

    assert cli.main() == 0
    markdown_path = out_dir / "demo-summary.md"
    assert markdown_path.exists()
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# Metadata Demo Summary" in markdown
    assert "## Top ranked demo tokens" in markdown


def test_run_openssl_metadata_demo_chain_cli_writes_metrics_outputs(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "openssl_metadata_demo"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_openssl_metadata_demo_chain",
            "--out-dir",
            str(out_dir),
            "--record-count",
            "4",
            "--epochs",
            "20",
            "--write-metrics-json",
            "--write-metrics-csv",
        ],
    )

    assert cli.main() == 0
    metrics = json.loads((out_dir / "demo-metrics.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((out_dir / "demo-metrics.csv").read_text(encoding="utf-8").splitlines()))
    assert metrics["format"] == "traceleak.metadata_demo_metrics.v1"
    assert metrics["phase"] == "P66"
    assert rows[0]["sample_id"] == metrics["sample_id"]


def test_run_openssl_metadata_demo_chain_cli_rejects_bad_record_count(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "openssl_metadata_demo"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_openssl_metadata_demo_chain",
            "--out-dir",
            str(out_dir),
            "--record-count",
            "3",
        ],
    )

    assert cli.main() == 1
