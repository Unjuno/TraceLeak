import json

from scripts import validate_openssl_materialization_approval_gate as cli
from traceleak.openssl_actual_execution_preflight import build_openssl_actual_execution_preflight_report
from traceleak.openssl_isolated_execution_plan import build_openssl_isolated_execution_plan
from traceleak.openssl_materialization_approval_gate import (
    build_openssl_materialization_approval_record,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_request_and_record() -> tuple[dict, dict]:
    preflight = build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )
    plan = build_openssl_isolated_execution_plan(preflight_report=preflight)
    request = build_openssl_reviewed_materialization_request(execution_plan=plan)
    record = build_openssl_materialization_approval_record(
        reviewed_request=request,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )
    return request, record


def test_validate_openssl_materialization_approval_gate_cli_accepts_valid_pair(
    tmp_path,
    monkeypatch,
) -> None:
    request, record = make_request_and_record()
    request_path = tmp_path / "request.json"
    record_path = tmp_path / "record.json"
    out = tmp_path / "gate.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    record_path.write_text(json.dumps(record), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_materialization_approval_gate",
            "--request",
            str(request_path),
            "--approval-record",
            str(record_path),
            "--out",
            str(out),
        ],
    )

    assert cli.main() == 0

    gate = json.loads(out.read_text(encoding="utf-8"))
    assert gate["format"] == "traceleak.openssl_materialization_approval_gate.v1"
    assert gate["status"] == "approval_gate_satisfied"
    assert gate["materialization_allowed"] is True
    assert gate["execution_allowed"] is False


def test_validate_openssl_materialization_approval_gate_cli_rejects_scope_mismatch(
    tmp_path,
    monkeypatch,
) -> None:
    request, record = make_request_and_record()
    record["approval_scope"] = "wrong_scope"
    request_path = tmp_path / "request.json"
    record_path = tmp_path / "record.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    record_path.write_text(json.dumps(record), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_materialization_approval_gate",
            "--request",
            str(request_path),
            "--approval-record",
            str(record_path),
        ],
    )

    assert cli.main() == 1
