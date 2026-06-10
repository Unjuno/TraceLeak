import pytest

from traceleak.model_results import (
    ModelResultError,
    attributions_from_model_result,
    model_result_summary,
    validate_model_result,
)


def valid_result() -> dict:
    return {
        "experiment_id": "exp_001_synthetic_generated",
        "target": "synthetic-leak",
        "view": "redacted",
        "model": {
            "name": "local-neural-placeholder",
            "type": "neural",
            "version": "local",
        },
        "metrics": {
            "test": {
                "accuracy": 0.875,
                "DeltaH": 4.0,
            }
        },
        "attributions": [
            {
                "group_id": "synthetic_branch_event",
                "group_type": "branch",
                "score": 3.0,
                "location": "examples/synthetic/target.py:19",
                "evidence": ["model_importance"],
            }
        ],
    }


def test_validate_model_result_accepts_valid_result() -> None:
    validate_model_result(valid_result())


def test_validate_model_result_rejects_raw_public_view() -> None:
    result = valid_result()
    result["view"] = "raw"
    with pytest.raises(ModelResultError):
        validate_model_result(result)


def test_validate_model_result_rejects_secret_equivalent_field() -> None:
    result = valid_result()
    result["value_raw"] = "not allowed"
    with pytest.raises(ModelResultError):
        validate_model_result(result)


def test_validate_model_result_rejects_invalid_metric_split() -> None:
    result = valid_result()
    result["metrics"] = {"deployment": {"accuracy": 1.0}}
    with pytest.raises(ModelResultError):
        validate_model_result(result)


def test_model_result_summary() -> None:
    summary = model_result_summary(valid_result())
    assert summary == {
        "experiment_id": "exp_001_synthetic_generated",
        "target": "synthetic-leak",
        "view": "redacted",
        "model_type": "neural",
        "metric_count": 1,
        "attribution_count": 1,
    }


def test_attributions_from_model_result() -> None:
    scores = attributions_from_model_result(valid_result())
    assert len(scores) == 1
    assert scores[0].group_id == "synthetic_branch_event"
    assert scores[0].contribution == pytest.approx(3.0)
