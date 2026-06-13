import json

from scripts import build_openssl_materialization_output_contract as cli
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


def test_build_openssl_materialization_output_contract_cli_writes_contract(
    tmp_path,
    monkeypatch,
) -> None:
    request, record = make_request_and_record()
    request_path = tmp_path / "request.json"
    record_path = tmp_path / "record.json"
    out = tmp_path / "contract.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    record_path.write_text(json.dumps(record), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_openssl_materialization_output_contract",
            "--request",
            str(request_path),
            "--approval-record",
            str(record_path),
            "--output-manifest-path",
            "artifacts/openssl-materialization-output-manifest.json",
            "--out",
            str(out),
        ],
    )

    assert cli.main() == 0

    contract = json.loads(out.read_text(encoding="utf-8"))
    assert contract["format"] == "traceleak.openssl_materialization_output_contract.v1"
    assert contract["status"] == "output_contract_ready"
    assert contract["mode"] == "contract_only"
    assert contract["output_generated"] is False
    assert contract["output_schema"]["redacted_metadata_only"] is True
    assert contract["output_schema"]["source_text_embedded"] is False
    assert contract["output_schema"]["diff_embedded"] is False
    assert contract["output_schema"]["commands_embedded"] is False
    assert contract["execution_allowed"] is False
