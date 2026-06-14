import pytest

from traceleak.model_sequence_nn import parse_model_sequence_nn_vectors
from traceleak.openssl_derived_metadata_adapter import (
    OpenSSLDerivedMetadataAdapterError,
    adapt_openssl_derived_metadata_to_model_sequence,
    validate_openssl_derived_metadata_input,
)
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate


def make_runtime_gate() -> dict:
    return build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )


def make_metadata_input() -> dict:
    return {
        "format": "traceleak.openssl_derived_metadata_input.v1",
        "source_pin_digest": "sha256:source-pin",
        "target_decision": "constant_time_helper_misuse_path",
        "metadata_only": True,
        "payload_free": True,
        "label_name": "metadata_bucket",
        "records": [
            {
                "run_id": "r0",
                "source_region_token": "ct_helper_family_a",
                "transition_token": "branch_symbolic_a",
                "label": "bucket_a",
            },
            {
                "run_id": "r1",
                "source_region_token": "ct_helper_family_b",
                "transition_token": "branch_symbolic_b",
                "label": "bucket_b",
            },
        ],
    }


def test_adapter_converts_symbolic_metadata_to_model_sequence() -> None:
    payload = adapt_openssl_derived_metadata_to_model_sequence(
        metadata_input=make_metadata_input(),
        runtime_gate=make_runtime_gate(),
    )

    assert payload["format"] == "traceleak.model_sequence.v1"
    assert payload["artifact_format"] == "traceleak.openssl_derived_metadata_model_sequence.v1"
    assert payload["target"] == "openssl-derived-metadata"
    assert payload["view"] == "meta"
    assert payload["run_count"] == 2
    vectors = parse_model_sequence_nn_vectors(payload)
    assert {vector.label for vector in vectors} == {"bucket_a", "bucket_b"}


def test_adapter_rejects_forbidden_payload_field() -> None:
    metadata = make_metadata_input()
    metadata["records"][0]["payload"] = {"forbidden": True}

    with pytest.raises(OpenSSLDerivedMetadataAdapterError, match="payload"):
        validate_openssl_derived_metadata_input(metadata)


def test_adapter_rejects_source_text() -> None:
    metadata = make_metadata_input()
    metadata["records"][0]["source_text"] = "not allowed"

    with pytest.raises(OpenSSLDerivedMetadataAdapterError, match="source_text"):
        validate_openssl_derived_metadata_input(metadata)


def test_adapter_rejects_single_label_input() -> None:
    metadata = make_metadata_input()
    metadata["records"][1]["label"] = "bucket_a"

    with pytest.raises(OpenSSLDerivedMetadataAdapterError, match="two labels"):
        validate_openssl_derived_metadata_input(metadata)
