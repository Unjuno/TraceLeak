import json

import pytest

from traceleak.metadata_symbolic_authoring import (
    MetadataSymbolicAuthoringError,
    build_symbolic_metadata_input,
    validate_symbolic_metadata_input,
    write_symbolic_metadata_input,
)
from traceleak.openssl_derived_metadata_adapter import adapt_openssl_derived_metadata_to_model_sequence
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate
from traceleak.model_sequence_nn import parse_model_sequence_nn_vectors


def symbolic_records() -> list[dict[str, str]]:
    return [
        {
            "source_region_token": "ct_helper_family_a",
            "transition_token": "branch_symbolic_a",
            "label": "bucket_a",
        },
        {
            "source_region_token": "ct_helper_family_a2",
            "transition_token": "branch_symbolic_a2",
            "label": "bucket_a",
        },
        {
            "source_region_token": "ct_helper_family_b",
            "transition_token": "branch_symbolic_b",
            "label": "bucket_b",
        },
        {
            "source_region_token": "ct_helper_family_b2",
            "transition_token": "branch_symbolic_b2",
            "label": "bucket_b",
        },
    ]


def test_symbolic_metadata_authoring_builds_adapter_input() -> None:
    payload = build_symbolic_metadata_input(records=symbolic_records())

    assert payload["format"] == "traceleak.openssl_derived_metadata_input.v1"
    assert payload["authoring_phase"] == "P80"
    assert payload["metadata_only"] is True
    assert payload["payload_free"] is True
    assert payload["label_name"] == "metadata_bucket"
    assert [record["run_id"] for record in payload["records"]] == [
        "symbolic-0000",
        "symbolic-0001",
        "symbolic-0002",
        "symbolic-0003",
    ]
    validate_symbolic_metadata_input(payload)


def test_symbolic_metadata_authoring_adapts_to_model_sequence() -> None:
    payload = build_symbolic_metadata_input(records=symbolic_records())
    gate = build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )

    sample = adapt_openssl_derived_metadata_to_model_sequence(
        metadata_input=payload,
        runtime_gate=gate,
    )
    parsed = parse_model_sequence_nn_vectors(sample)

    assert sample["format"] == "traceleak.model_sequence.v1"
    assert sample["run_count"] == 4
    assert len(parsed.labels) == 4
    assert set(parsed.labels) == {"bucket_a", "bucket_b"}


def test_symbolic_metadata_authoring_writes_json(tmp_path) -> None:
    payload = build_symbolic_metadata_input(records=symbolic_records())
    path = tmp_path / "symbolic-metadata.json"

    write_symbolic_metadata_input(path, payload)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["authoring_phase"] == "P80"
    assert loaded["records"][0]["source_region_token"] == "ct_helper_family_a"


def test_symbolic_metadata_authoring_rejects_unbalanced_labels() -> None:
    records = symbolic_records()[:3]

    with pytest.raises(MetadataSymbolicAuthoringError, match="at least four"):
        build_symbolic_metadata_input(records=records)


def test_symbolic_metadata_authoring_rejects_one_sample_label() -> None:
    records = symbolic_records()
    records[-1] = {
        "source_region_token": "ct_helper_family_c",
        "transition_token": "branch_symbolic_c",
        "label": "bucket_c",
    }

    with pytest.raises(MetadataSymbolicAuthoringError, match="at least two records"):
        build_symbolic_metadata_input(records=records)


def test_symbolic_metadata_authoring_rejects_forbidden_payload() -> None:
    records = symbolic_records()
    records[0]["payload"] = "blocked"

    with pytest.raises(MetadataSymbolicAuthoringError, match="payload"):
        build_symbolic_metadata_input(records=records)
