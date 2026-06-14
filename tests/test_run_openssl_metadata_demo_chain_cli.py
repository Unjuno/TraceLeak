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
