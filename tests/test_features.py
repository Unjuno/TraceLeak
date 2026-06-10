import pytest

from traceleak.features import FeatureExtractionError, build_feature_matrix, extract_feature_vector


def redacted_run() -> dict:
    return {
        "run_id": "synthetic_000001",
        "target": "synthetic-example",
        "target_version": "v0",
        "view": "redacted",
        "events": [
            {
                "step": 1,
                "phase": "synthetic_phase",
                "function": "synthetic_fn",
                "file": "examples/synthetic/target.c",
                "line": 21,
                "event_type": "branch",
                "name": "example_branch_event",
                "value_redacted": {"branch_taken": True, "bucket": "1-3", "count": 2},
            }
        ],
    }


def test_extract_feature_vector_contains_event_tokens() -> None:
    features = extract_feature_vector(redacted_run())
    assert features["run.view=redacted"] == pytest.approx(1.0)
    assert features["event_type=branch"] == pytest.approx(1.0)
    assert features["phase=synthetic_phase"] == pytest.approx(1.0)
    assert features["function=synthetic_fn"] == pytest.approx(1.0)
    assert features["location=examples/synthetic/target.c:21"] == pytest.approx(1.0)


def test_extract_feature_vector_encodes_redacted_values() -> None:
    features = extract_feature_vector(redacted_run())
    assert features[
        "event_value:branch:synthetic_phase:synthetic_fn:example_branch_event:value_redacted.branch_taken"
    ] == pytest.approx(1.0)
    assert features[
        "event_value:branch:synthetic_phase:synthetic_fn:example_branch_event:value_redacted.count"
    ] == pytest.approx(2.0)
    assert features[
        "event_value:branch:synthetic_phase:synthetic_fn:example_branch_event:value_redacted.bucket=1-3"
    ] == pytest.approx(1.0)


def test_extract_feature_vector_rejects_raw_by_default() -> None:
    run = redacted_run()
    run["view"] = "raw"
    with pytest.raises(FeatureExtractionError):
        extract_feature_vector(run)


def test_extract_feature_vector_allows_raw_when_explicit() -> None:
    run = redacted_run()
    run["view"] = "raw"
    features = extract_feature_vector(run, allow_raw=True)
    assert features["run.view=raw"] == pytest.approx(1.0)


def test_build_feature_matrix() -> None:
    names, matrix = build_feature_matrix([redacted_run()])
    assert "run.view=redacted" in names
    assert len(matrix) == 1
    assert len(matrix[0]) == len(names)


def test_build_feature_matrix_rejects_empty_input() -> None:
    with pytest.raises(FeatureExtractionError):
        build_feature_matrix([])
