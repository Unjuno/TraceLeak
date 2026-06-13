import json

from scripts import build_openssl_actual_execution_preflight as cli


def test_build_openssl_actual_execution_preflight_cli_writes_blocked_report(
    tmp_path,
    monkeypatch,
) -> None:
    out = tmp_path / "preflight.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_openssl_actual_execution_preflight",
            "--out",
            str(out),
            "--source-pin-digest",
            "sha256:source-pin",
            "--trace-contract-digest",
            "sha256:trace-contract",
            "--workspace-root",
            "C:/tmp/traceleak-openssl-workspace",
            "--cleanup-plan",
            "remove isolated workspace after review",
        ],
    )

    assert cli.main() == 0

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["format"] == "traceleak.openssl_actual_execution_preflight.v1"
    assert report["blockers"] == []
    assert report["execution_allowed"] is False
    assert report["compile_allowed"] is False
    assert report["patch_application_allowed"] is False
    assert report["raw_capture_allowed"] is False
