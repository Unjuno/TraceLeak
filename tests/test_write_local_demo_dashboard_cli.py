import json

from scripts import write_local_demo_dashboard as cli


def test_write_local_demo_dashboard_cli_writes_json_and_markdown(tmp_path, monkeypatch) -> None:
    root_dir = tmp_path / "reports" / "local"
    (root_dir / "openssl_metadata_demo").mkdir(parents=True)
    (root_dir / "symbolic_metadata_demo").mkdir(parents=True)
    (root_dir / "openssl_metadata_demo" / "demo-summary.json").write_text("{}\n", encoding="utf-8")
    (root_dir / "symbolic_metadata_demo" / "symbolic-demo-summary.json").write_text("{}\n", encoding="utf-8")
    out_path = tmp_path / "local-demo-dashboard.json"
    markdown_path = tmp_path / "local-demo-dashboard.md"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_local_demo_dashboard",
            "--root-dir",
            str(root_dir),
            "--out",
            str(out_path),
            "--markdown-out",
            str(markdown_path),
        ],
    )

    assert cli.main() == 0
    dashboard = json.loads(out_path.read_text(encoding="utf-8"))
    assert dashboard["format"] == "traceleak.local_demo_dashboard.v1"
    assert dashboard["phase"] == "P90"
    assert dashboard["present_count"] == 2
    assert markdown_path.read_text(encoding="utf-8").startswith("# Local Demo Dashboard")


def test_write_local_demo_dashboard_cli_rejects_bad_expected_path(tmp_path, monkeypatch) -> None:
    out_path = tmp_path / "local-demo-dashboard.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "write_local_demo_dashboard",
            "--root-dir",
            str(tmp_path / "missing"),
            "--out",
            str(out_path),
        ],
    )

    assert cli.main() == 0
    assert out_path.exists()
