import json

import pytest

from traceleak.model_sequence_nn import parse_model_sequence_nn_vectors
from traceleak.openssl_derived_metadata_adapter import adapt_openssl_derived_metadata_to_model_sequence
from traceleak.openssl_derived_metadata_profile import (
    OPENSSL_DERIVED_METADATA_PROFILE_FORMAT,
    OpenSSLDerivedMetadataProfileError,
    adapt_openssl_derived_metadata_profile_to_adapter_input,
    build_openssl_derived_metadata_profile_input,
    default_openssl_derived_metadata_profile_records,
    validate_openssl_derived_metadata_profile_input,
    write_openssl_derived_metadata_profile_adapter_input,
    write_openssl_derived_metadata_profile_input,
)
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate


def profile_input(records=None):
    return build_openssl_derived_metadata_profile_input(records=records)


def test_profile_builds_minimal_balanced_input() -> None:
    payload = profile_input()

    assert payload["format"] == OPENSSL_DERIVED_METADATA_PROFILE_FORMAT
    assert payload["phase"] == "P96"
    assert payload["metadata_only"] is True
    assert payload["payload_free"] is True
    assert payload["public_safe"] is True
    assert payload["target_decision"] == "constant_time_helper_misuse_path"
    assert len(payload["records"]) == 4
    validate_openssl_derived_metadata_profile_input(payload)


def test_profile_accepts_optional_safe_record_fields() -> None:
    payload = profile_input()

    first = payload["records"][0]

    assert first["function_token"] == "bn_mod_exp_family"
    assert first["metadata_tags"] == {"bucket": "a", "profile": "level6"}


def test_profile_writes_profile_and_adapter_json(tmp_path) -> None:
    payload = profile_input()
    adapter_input = adapt_openssl_derived_metadata_profile_to_adapter_input(payload)
    profile_path = tmp_path / "profile-input.json"
    adapter_path = tmp_path / "adapter-input.json"

    write_openssl_derived_metadata_profile_input(profile_path, payload)
    write_openssl_derived_metadata_profile_adapter_input(adapter_path, adapter_input)

    assert json.loads(profile_path.read_text(encoding="utf-8"))["format"] == OPENSSL_DERIVED_METADATA_PROFILE_FORMAT
    assert json.loads(adapter_path.read_text(encoding="utf-8"))["format"] == "traceleak.openssl_derived_metadata_input.v1"


def test_profile_bridges_to_model_sequence() -> None:
    payload = profile_input()
    adapter_input = adapt_openssl_derived_metadata_profile_to_adapter_input(payload)
    gate = build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )

    sample = adapt_openssl_derived_metadata_to_model_sequence(
        metadata_input=adapter_input,
        runtime_gate=gate,
    )
    vectors = parse_model_sequence_nn_vectors(sample)
    labels = [item.label for item in vectors]

    assert sample["format"] == "traceleak.model_sequence.v1"
    assert sample["run_count"] == 4
    assert len(vectors) == 4
    assert set(labels) == {"candidate_a", "candidate_b"}


def test_profile_rejects_missing_required_top_level_field() -> None:
    payload = profile_input()
    del payload["source_pin_digest"]

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="missing required"):
        validate_openssl_derived_metadata_profile_input(payload)


def test_profile_rejects_missing_required_record_field() -> None:
    records = default_openssl_derived_metadata_profile_records()
    del records[0]["transition_token"]

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="missing fields"):
        build_openssl_derived_metadata_profile_input(records=records)


def test_profile_rejects_forbidden_field_recursively() -> None:
    records = default_openssl_derived_metadata_profile_records()
    records[0]["metadata_tags"]["payload"] = "blocked"

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="payload"):
        build_openssl_derived_metadata_profile_input(records=records)


def test_profile_rejects_duplicate_run_id() -> None:
    records = default_openssl_derived_metadata_profile_records()
    records[1]["run_id"] = records[0]["run_id"]

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="unique"):
        build_openssl_derived_metadata_profile_input(records=records)


def test_profile_rejects_unstable_run_id() -> None:
    records = default_openssl_derived_metadata_profile_records()
    records[0]["run_id"] = "bad run id"

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="unsupported characters"):
        build_openssl_derived_metadata_profile_input(records=records)


def test_profile_rejects_one_sample_label() -> None:
    records = default_openssl_derived_metadata_profile_records()
    records[-1]["label"] = "candidate_c"

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="at least two records"):
        build_openssl_derived_metadata_profile_input(records=records)


def test_profile_rejects_single_label() -> None:
    records = default_openssl_derived_metadata_profile_records()
    for record in records:
        record["label"] = "candidate_a"

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="at least two labels"):
        build_openssl_derived_metadata_profile_input(records=records)


def test_profile_rejects_path_like_token() -> None:
    records = default_openssl_derived_metadata_profile_records()
    records[0]["source_region_token"] = "../region"

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="unsupported characters"):
        build_openssl_derived_metadata_profile_input(records=records)


def test_profile_rejects_false_safety_flags() -> None:
    payload = profile_input()
    payload["metadata_only"] = False

    with pytest.raises(OpenSSLDerivedMetadataProfileError, match="metadata_only"):
        validate_openssl_derived_metadata_profile_input(payload)
