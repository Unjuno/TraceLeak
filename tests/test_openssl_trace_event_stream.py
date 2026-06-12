import copy
from pathlib import Path

import pytest

from scripts import build_openssl_trace_sample, openssl_trace_events_to_report, validate_openssl_trace_events
from traceleak.openssl_trace_acceptance import validate_openssl_trace_sample_acceptance
from traceleak.openssl_trace_contract import load_openssl_trace_contract
from traceleak.openssl_trace_event_stream import (
    OpenSSLTraceEventStreamError,
    load_openssl_redacted_event_stream,
    openssl_redacted_event_stream_report_dict,
    openssl_redacted_event_stream_report_markdown,
    validate_openssl_redacted_event_stream,
)
from traceleak.openssl_trace_sample_builder import build_openssl_model_sequence_sample

CONTRACT_PATH = Path("examples/openssl_trace_contract/openssl_rsa_keygen_trace_contract_sample.json")
STREAM_PATH = Path("examples/openssl_trace_events/openssl_rsa_keygen_redacted_event_stream_sample.jsonl")


def contract() -> dict:
    return load_openssl_trace_contract(CONTRACT_PATH)


def runs() -> list[dict]:
    return load_openssl_redacted_event_stream(STREAM_PATH)


def test_load_and_validate_openssl_redacted_event_stream_sample() -> None:
    loaded_runs = runs()

    validate_openssl_redacted_event_stream(contract(), loaded_runs)

    assert len(loaded_runs) == 4
    assert sum(len(run["events"]) for run in loaded_runs) == 12
    assert loaded_runs[0]["view"] == "redacted"
    assert loaded_runs[0]["metadata"]["raw_secret_captured"] is False


def test_openssl_redacted_event_stream_report_summarizes_boundary() -> None:
    report = openssl_redacted_event_stream_report_dict(contract(), runs())
    markdown = openssl_redacted_event_stream_report_markdown(report)

    assert report["status"] == "accepted_redacted_openssl_event_stream"
    assert report["run_count"] == 4
    assert report["event_count"] == 12
    assert report["raw_secret_captured"] is False
    assert "Status: `accepted_redacted_openssl_event_stream`" in markdown
    assert "Raw secret captured: `false`" in markdown
    assert "Events: `12`" in markdown


def test_event_stream_rejects_raw_view() -> None:
    bad_runs = runs()
    bad_runs[0] = copy.deepcopy(bad_runs[0])
    bad_runs[0]["view"] = "raw"

    with pytest.raises(OpenSSLTraceEventStreamError, match="view"):
        validate_openssl_redacted_event_stream(contract(), bad_runs)


def test_event_stream_rejects_source_pin_mismatch() -> None:
    bad_runs = runs()
    bad_runs[0] = copy.deepcopy(bad_runs[0])
    bad_runs[0]["metadata"]["source_pin"] = "sha256:other"

    with pytest.raises(OpenSSLTraceEventStreamError, match="source_pin"):
        validate_openssl_redacted_event_stream(contract(), bad_runs)


def test_event_stream_rejects_raw_secret_capture_metadata() -> None:
    bad_runs = runs()
    bad_runs[0] = copy.deepcopy(bad_runs[0])
    bad_runs[0]["metadata"]["raw_secret_captured"] = True

    with pytest.raises(OpenSSLTraceEventStreamError, match="raw_secret_captured"):
        validate_openssl_redacted_event_stream(contract(), bad_runs)


def test_event_stream_rejects_disallowed_nested_field() -> None:
    bad_runs = runs()
    bad_runs[0] = copy.deepcopy(bad_runs[0])
    bad_runs[0]["events"][0]["metadata"] = {"prime_candidate": "redacted"}

    with pytest.raises(OpenSSLTraceEventStreamError, match="prime_candidate"):
        validate_openssl_redacted_event_stream(contract(), bad_runs)


def test_event_stream_sample_build_acceptance_chain() -> None:
    sample = build_openssl_model_sequence_sample(
        contract=contract(),
        runs=runs(),
        input_name=str(STREAM_PATH),
    )

    assert sample["run_count"] == 4
    assert sample["actual_trace_derived"] is True
    assert sample["raw_secret_captured"] is False
    validate_openssl_trace_sample_acceptance(contract(), sample)


def test_validate_openssl_trace_events_cli_accepts_sample(capsys: pytest.CaptureFixture[str]) -> None:
    old_parse = validate_openssl_trace_events.parse_args
    validate_openssl_trace_events.parse_args = lambda: type(
        "Args",
        (),
        {"contract": CONTRACT_PATH, "input_path": STREAM_PATH},
    )()
    try:
        assert validate_openssl_trace_events.main() == 0
    finally:
        validate_openssl_trace_events.parse_args = old_parse

    assert "valid OpenSSL redacted event stream" in capsys.readouterr().out


def test_openssl_trace_events_to_report_cli_writes_markdown(tmp_path: Path) -> None:
    out = tmp_path / "event_stream.md"
    old_parse = openssl_trace_events_to_report.parse_args
    openssl_trace_events_to_report.parse_args = lambda: type(
        "Args",
        (),
        {"contract": CONTRACT_PATH, "input_path": STREAM_PATH, "output_path": out, "format": "md"},
    )()
    try:
        assert openssl_trace_events_to_report.main() == 0
    finally:
        openssl_trace_events_to_report.parse_args = old_parse

    markdown = out.read_text(encoding="utf-8")
    assert "TraceLeak OpenSSL Redacted Event Stream Report" in markdown
    assert "accepted_redacted_openssl_event_stream" in markdown


def test_build_openssl_trace_sample_cli_accepts_stream_fixture(tmp_path: Path) -> None:
    out = tmp_path / "model_sequence.json"
    old_parse = build_openssl_trace_sample.parse_args
    build_openssl_trace_sample.parse_args = lambda: type(
        "Args",
        (),
        {"contract": CONTRACT_PATH, "input_path": STREAM_PATH, "output_path": out, "label_key": None},
    )()
    try:
        assert build_openssl_trace_sample.main() == 0
    finally:
        build_openssl_trace_sample.parse_args = old_parse

    built = out.read_text(encoding="utf-8")
    assert "traceleak.model_sequence.v1" in built
    assert "actual_trace_derived" in built
