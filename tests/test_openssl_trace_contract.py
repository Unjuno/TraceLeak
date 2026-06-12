import copy
import json
from pathlib import Path

import pytest

from scripts import openssl_trace_contract_to_report, validate_openssl_trace_contract
from traceleak.openssl_trace_contract import (
    MODEL_SEQUENCE_FORMAT,
    OPENSSL_TRACE_CONTRACT_FORMAT,
    OpenSSLTraceContractError,
    load_openssl_trace_contract,
    openssl_trace_contract_report_dict,
    openssl_trace_contract_report_markdown,
    validate_openssl_trace_contract as validate_contract,
)

SAMPLE = Path("examples/openssl_trace_contract/openssl_rsa_keygen_trace_contract_sample.json")


def load_sample() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def test_load_openssl_trace_contract_sample() -> None:
    contract = load_openssl_trace_contract(SAMPLE)

    assert contract["format"] == OPENSSL_TRACE_CONTRACT_FORMAT
    assert contract["target"] == "openssl-rsa-keygen"
    assert contract["actual_trace_derived"] is True
    assert contract["trace_collection_mode"] == "redacted"
    assert contract["raw_secret_captured"] is False
    assert contract["collector"]["produces_format"] == MODEL_SEQUENCE_FORMAT


def test_openssl_trace_contract_report_marks_contract_not_executed() -> None:
    report = openssl_trace_contract_report_dict(load_sample())
    markdown = openssl_trace_contract_report_markdown(report)

    assert report["status"] == "contract_ready_not_executed"
    assert report["execution_allowed"] is False
    assert report["raw_secret_captured"] is False
    assert "Status: `contract_ready_not_executed`" in markdown
    assert "Execution allowed by this validator: `false`" in markdown
    assert "Raw secret captured: `false`" in markdown
    assert "Produces format: `traceleak.model_sequence.v1`" in markdown


def test_openssl_trace_contract_rejects_execution_allowed() -> None:
    contract = load_sample()
    contract["execution_allowed"] = True

    with pytest.raises(OpenSSLTraceContractError, match="execution_allowed"):
        validate_contract(contract)


def test_openssl_trace_contract_rejects_raw_secret_capture() -> None:
    contract = load_sample()
    contract["raw_secret_captured"] = True

    with pytest.raises(OpenSSLTraceContractError, match="raw_secret_captured"):
        validate_contract(contract)


def test_openssl_trace_contract_rejects_raw_trace_retention() -> None:
    contract = load_sample()
    contract["safety"]["raw_trace_retention"] = "allowed"

    with pytest.raises(OpenSSLTraceContractError, match="raw_trace_retention"):
        validate_contract(contract)


def test_openssl_trace_contract_rejects_missing_record_field() -> None:
    contract = load_sample()
    contract["collector"] = copy.deepcopy(contract["collector"])
    contract["collector"]["required_record_fields"].remove("token_counts")

    with pytest.raises(OpenSSLTraceContractError, match="token_counts"):
        validate_contract(contract)


def test_openssl_trace_contract_rejects_forbidden_value_channel() -> None:
    contract = load_sample()
    contract["safety"] = copy.deepcopy(contract["safety"])
    contract["safety"]["allowed_value_channels"].append("raw_secret")

    with pytest.raises(OpenSSLTraceContractError, match="raw_secret"):
        validate_contract(contract)


def test_validate_openssl_trace_contract_cli_accepts_sample(capsys: pytest.CaptureFixture[str]) -> None:
    old_parse = validate_openssl_trace_contract.parse_args
    validate_openssl_trace_contract.parse_args = lambda: type("Args", (), {"path": SAMPLE})()
    try:
        assert validate_openssl_trace_contract.main() == 0
    finally:
        validate_openssl_trace_contract.parse_args = old_parse

    assert "valid OpenSSL trace contract" in capsys.readouterr().out


def test_openssl_trace_contract_to_report_cli_writes_markdown(tmp_path: Path) -> None:
    out = tmp_path / "openssl_trace_contract.md"
    old_parse = openssl_trace_contract_to_report.parse_args
    openssl_trace_contract_to_report.parse_args = lambda: type(
        "Args",
        (),
        {"input_path": SAMPLE, "output_path": out, "format": "md"},
    )()
    try:
        assert openssl_trace_contract_to_report.main() == 0
    finally:
        openssl_trace_contract_to_report.parse_args = old_parse

    markdown = out.read_text(encoding="utf-8")
    assert "TraceLeak OpenSSL Trace Contract Report" in markdown
    assert "contract_ready_not_executed" in markdown
    assert "Raw secret captured: `false`" in markdown
}
