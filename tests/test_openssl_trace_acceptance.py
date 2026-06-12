import copy
import json
from pathlib import Path

import pytest

from scripts import openssl_trace_sample_to_report, validate_openssl_trace_sample
from traceleak.openssl_trace_acceptance import (
    OpenSSLTraceAcceptanceError,
    openssl_trace_sample_acceptance_report_dict,
    openssl_trace_sample_acceptance_report_markdown,
    validate_openssl_trace_sample_acceptance,
)
from traceleak.openssl_trace_contract import load_openssl_trace_contract

CONTRACT_PATH = Path("examples/openssl_trace_contract/openssl_rsa_keygen_trace_contract_sample.json")


def contract() -> dict:
    return load_openssl_trace_contract(CONTRACT_PATH)


def accepted_sample() -> dict:
    c = contract()
    return {
        "format": "traceleak.model_sequence.v1",
        "input": "openssl-rsa-keygen-redacted-model-sequence",
        "run_count": 4,
        "public_safe": True,
        "include_counts": True,
        "include_redacted_values": False,
        "label_name": "rsa_keygen_attempt_bucket",
        "contains_lab_only_labels": True,
        "target": c["target"],
        "target_version": c["target_version"],
        "source_pin": c["source_pin"],
        "build_id": c["build_id"],
        "view": "redacted",
        "validation_scope": "actual_trace_derived",
        "actual_trace_derived": True,
        "trace_collection_mode": "redacted",
        "raw_secret_captured": False,
        "notes": ["Contract-compatible acceptance fixture; not produced by running OpenSSL in tests."],
        "records": [
            {
                "run_id": "openssl_redacted_seq_000001",
                "target": c["target"],
                "target_version": c["target_version"],
                "view": "redacted",
                "label": "0",
                "token_counts": {
                    "event_type=phase": 1.0,
                    "event_type=branch": 2.0,
                    "phase=candidate_generation": 1.0,
                    "context_token=candidate_filter:ossl_rsa_keygen": 3.0,
                    "event_token=loop:candidate_filter:ossl_rsa_keygen:bn_prime_trial_division": 3.0,
                    "source_token=crypto/rsa/rsa_gen.c:100:ossl_rsa_keygen:bn_prime_trial_division": 3.0,
                },
            },
            {
                "run_id": "openssl_redacted_seq_000002",
                "target": c["target"],
                "target_version": c["target_version"],
                "view": "redacted",
                "label": "1",
                "token_counts": {
                    "event_type=phase": 1.0,
                    "event_type=branch": 2.0,
                    "phase=candidate_generation": 1.0,
                    "context_token=candidate_filter:ossl_rsa_keygen": 5.0,
                    "event_token=loop:candidate_filter:ossl_rsa_keygen:bn_prime_trial_division": 5.0,
                    "source_token=crypto/rsa/rsa_gen.c:100:ossl_rsa_keygen:bn_prime_trial_division": 5.0,
                },
            },
            {
                "run_id": "openssl_redacted_seq_000003",
                "target": c["target"],
                "target_version": c["target_version"],
                "view": "redacted",
                "label": "0",
                "token_counts": {
                    "event_type=phase": 1.0,
                    "event_type=branch": 2.0,
                    "phase=candidate_generation": 1.0,
                    "context_token=candidate_filter:ossl_rsa_keygen": 4.0,
                    "event_token=loop:candidate_filter:ossl_rsa_keygen:bn_prime_trial_division": 4.0,
                    "source_token=crypto/rsa/rsa_gen.c:100:ossl_rsa_keygen:bn_prime_trial_division": 4.0,
                },
            },
            {
                "run_id": "openssl_redacted_seq_000004",
                "target": c["target"],
                "target_version": c["target_version"],
                "view": "redacted",
                "label": "1",
                "token_counts": {
                    "event_type=phase": 1.0,
                    "event_type=branch": 2.0,
                    "phase=candidate_generation": 1.0,
                    "context_token=candidate_filter:ossl_rsa_keygen": 6.0,
                    "event_token=loop:candidate_filter:ossl_rsa_keygen:bn_prime_trial_division": 6.0,
                    "source_token=crypto/rsa/rsa_gen.c:100:ossl_rsa_keygen:bn_prime_trial_division": 6.0,
                },
            },
        ],
    }


def write_sample(path: Path, sample: dict) -> None:
    path.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_accepts_contract_compatible_redacted_model_sequence_sample() -> None:
    validate_openssl_trace_sample_acceptance(contract(), accepted_sample())


def test_acceptance_report_summarizes_safe_sample() -> None:
    report = openssl_trace_sample_acceptance_report_dict(contract(), accepted_sample())
    markdown = openssl_trace_sample_acceptance_report_markdown(report)

    assert report["status"] == "accepted_redacted_model_sequence_sample"
    assert report["record_count"] == 4
    assert report["raw_secret_captured"] is False
    assert report["feature_count"] == 6
    assert "Status: `accepted_redacted_model_sequence_sample`" in markdown
    assert "Raw secret captured: `false`" in markdown
    assert "Features: `6`" in markdown


def test_rejects_target_mismatch() -> None:
    sample = accepted_sample()
    sample["target"] = "toy-rsa-like-count-pattern"

    with pytest.raises(OpenSSLTraceAcceptanceError, match="sample.target"):
        validate_openssl_trace_sample_acceptance(contract(), sample)


def test_rejects_non_redacted_view() -> None:
    sample = accepted_sample()
    sample["view"] = "raw"

    with pytest.raises(OpenSSLTraceAcceptanceError, match="sample.view"):
        validate_openssl_trace_sample_acceptance(contract(), sample)


def test_rejects_raw_secret_capture_flag() -> None:
    sample = accepted_sample()
    sample["raw_secret_captured"] = True

    with pytest.raises(OpenSSLTraceAcceptanceError, match="raw secrets"):
        validate_openssl_trace_sample_acceptance(contract(), sample)


def test_rejects_forbidden_token_channel() -> None:
    sample = accepted_sample()
    sample["records"][0]["token_counts"]["raw_secret=p"] = 1.0

    with pytest.raises(OpenSSLTraceAcceptanceError, match="channel not allowed"):
        validate_openssl_trace_sample_acceptance(contract(), sample)


def test_rejects_disallowed_token_name() -> None:
    sample = accepted_sample()
    sample["records"][0]["token_counts"]["event_token=private_key_branch"] = 1.0

    with pytest.raises(OpenSSLTraceAcceptanceError, match="private_key"):
        validate_openssl_trace_sample_acceptance(contract(), sample)


def test_rejects_missing_record_field() -> None:
    sample = accepted_sample()
    sample["records"][0] = copy.deepcopy(sample["records"][0])
    sample["records"][0].pop("token_counts")

    with pytest.raises(OpenSSLTraceAcceptanceError, match="token_counts"):
        validate_openssl_trace_sample_acceptance(contract(), sample)


def test_validate_openssl_trace_sample_cli_accepts_fixture(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample_path = tmp_path / "accepted_sample.json"
    write_sample(sample_path, accepted_sample())
    old_parse = validate_openssl_trace_sample.parse_args
    validate_openssl_trace_sample.parse_args = lambda: type(
        "Args",
        (),
        {"contract": CONTRACT_PATH, "sample": sample_path},
    )()
    try:
        assert validate_openssl_trace_sample.main() == 0
    finally:
        validate_openssl_trace_sample.parse_args = old_parse

    assert "accepted OpenSSL trace-derived sample" in capsys.readouterr().out


def test_openssl_trace_sample_to_report_cli_writes_markdown(tmp_path: Path) -> None:
    sample_path = tmp_path / "accepted_sample.json"
    report_path = tmp_path / "acceptance.md"
    write_sample(sample_path, accepted_sample())
    old_parse = openssl_trace_sample_to_report.parse_args
    openssl_trace_sample_to_report.parse_args = lambda: type(
        "Args",
        (),
        {"contract": CONTRACT_PATH, "sample": sample_path, "output_path": report_path, "format": "md"},
    )()
    try:
        assert openssl_trace_sample_to_report.main() == 0
    finally:
        openssl_trace_sample_to_report.parse_args = old_parse

    markdown = report_path.read_text(encoding="utf-8")
    assert "TraceLeak OpenSSL Trace Sample Acceptance Report" in markdown
    assert "accepted_redacted_model_sequence_sample" in markdown
    assert "Raw secret captured: `false`" in markdown
