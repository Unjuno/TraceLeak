import copy
import json
from pathlib import Path

import pytest

from traceleak.model_sequence_boundary import (
    ModelSequenceBoundaryError,
    attach_model_sequence_boundary,
    model_sequence_sample_boundary,
    validate_model_sequence_sample_boundary,
)
from traceleak.model_sequence_comparison import compare_model_sequence_nn_to_baseline
from traceleak.model_sequence_comparison_reporting import (
    model_sequence_comparison_report_dict,
    model_sequence_comparison_report_markdown,
)


def load_sample() -> dict:
    return json.loads(
        Path("examples/toy_rsa_like/model_sequence_nn_count_pattern_sample.json").read_text(
            encoding="utf-8"
        )
    )


def actual_trace_sample() -> dict:
    data = copy.deepcopy(load_sample())
    data.update(
        {
            "target": "openssl-rsa-keygen",
            "target_version": "openssl-3.x-test-pin",
            "source_pin": "sha256:source-test-pin",
            "build_id": "openssl-local-redacted-build-001",
            "validation_scope": "actual_trace_derived",
            "actual_trace_derived": True,
            "trace_collection_mode": "redacted",
            "raw_secret_captured": False,
            "public_safe": True,
        }
    )
    return data


def test_missing_boundary_defaults_to_toy_local_validation() -> None:
    boundary = model_sequence_sample_boundary(load_sample())

    assert boundary["validation_scope"] == "toy_local_validation"
    assert boundary["actual_trace_derived"] is False
    assert boundary["trace_collection_mode"] == "not_applicable"
    assert boundary["raw_secret_captured"] is False
    assert boundary["public_safe"] is True


def test_actual_trace_boundary_requires_redacted_public_safe_metadata() -> None:
    boundary = validate_model_sequence_sample_boundary(actual_trace_sample())

    assert boundary["validation_scope"] == "actual_trace_derived"
    assert boundary["actual_trace_derived"] is True
    assert boundary["trace_collection_mode"] == "redacted"
    assert boundary["raw_secret_captured"] is False
    assert boundary["target_version"] == "openssl-3.x-test-pin"
    assert boundary["source_pin"] == "sha256:source-test-pin"
    assert boundary["build_id"] == "openssl-local-redacted-build-001"


def test_actual_trace_boundary_rejects_raw_secret_capture() -> None:
    data = actual_trace_sample()
    data["raw_secret_captured"] = True

    with pytest.raises(ModelSequenceBoundaryError, match="raw secrets"):
        validate_model_sequence_sample_boundary(data)


def test_actual_trace_boundary_rejects_non_redacted_collection() -> None:
    data = actual_trace_sample()
    data["trace_collection_mode"] = "raw"

    with pytest.raises(ModelSequenceBoundaryError, match="trace_collection_mode=redacted"):
        validate_model_sequence_sample_boundary(data)


def test_actual_trace_boundary_rejects_missing_build_id() -> None:
    data = actual_trace_sample()
    data["build_id"] = "unknown"

    with pytest.raises(ModelSequenceBoundaryError, match="build_id"):
        validate_model_sequence_sample_boundary(data)


def test_attach_model_sequence_boundary_sets_result_fields() -> None:
    result = attach_model_sequence_boundary({"result_type": "example"}, actual_trace_sample())

    assert result["validation_scope"] == "actual_trace_derived"
    assert result["actual_trace_derived"] is True
    assert result["trace_collection_mode"] == "redacted"
    assert result["raw_secret_captured"] is False


def test_comparison_propagates_toy_boundary_defaults() -> None:
    result = compare_model_sequence_nn_to_baseline(load_sample(), epochs=40, learning_rate=0.8)

    assert result["validation_scope"] == "toy_local_validation"
    assert result["actual_trace_derived"] is False
    assert result["trace_collection_mode"] == "not_applicable"
    assert result["raw_secret_captured"] is False


def test_report_renders_actual_trace_boundary_metadata() -> None:
    result = compare_model_sequence_nn_to_baseline(actual_trace_sample(), epochs=40, learning_rate=0.8)
    report = model_sequence_comparison_report_dict(result)
    markdown = model_sequence_comparison_report_markdown(report)

    assert report["validation_scope"] == "actual_trace_derived"
    assert report["actual_trace_derived"] is True
    assert report["trace_collection_mode"] == "redacted"
    assert "Validation scope: `actual_trace_derived`" in markdown
    assert "Actual trace derived: `true`" in markdown
    assert "Trace collection mode: `redacted`" in markdown
    assert "Raw secret captured: `false`" in markdown
    assert "Target version: `openssl-3.x-test-pin`" in markdown
    assert "Source pin: `sha256:source-test-pin`" in markdown
    assert "Build ID: `openssl-local-redacted-build-001`" in markdown
