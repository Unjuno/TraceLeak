import json

from scripts import build_openssl_reviewed_materialization_request as cli


def test_build_openssl_reviewed_materialization_request_cli_writes_request(
    tmp_path,
    monkeypatch,
) -> None:
    out = tmp_path / "request.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_openssl_reviewed_materialization_request",
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

    request = json.loads(out.read_text(encoding="utf-8"))
    assert request["format"] == "traceleak.openssl_reviewed_materialization_request.v1"
    assert request["status"] == "request_draft"
    assert request["mode"] == "request_only"
    assert request["source_text_embedded"] is False
    assert request["diff_embedded"] is False
    assert request["commands_embedded"] is False
    assert request["materialization_allowed"] is False
    assert request["patch_application_allowed"] is False
    assert request["compile_allowed"] is False
    assert request["execution_allowed"] is False
    assert request["raw_capture_allowed"] is False
