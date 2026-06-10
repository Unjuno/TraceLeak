import pytest

from traceleak.model_reporting import ModelReportingError, model_result_to_report


def model_result() -> dict:
    return {
        "experiment_id": "exp_001_synthetic_generated",
        "target": "synthetic-leak",
        "view": "redacted",
        "model": {"name": "placeholder", "type": "neural"},
        "metrics": {"test": {"DeltaH": 4.0, "accuracy": 0.875}},
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


def test_model_result_to_report() -> None:
    report = model_result_to_report(model_result())
    assert report["target"] == "synthetic-leak"
    assert report["view"] == "redacted"
    assert report["metric"] == "DeltaH"
    assert report["score"] == pytest.approx(4.0)
    assert report["attributions"][0]["group_id"] == "synthetic_branch_event"


def test_model_result_to_report_selects_metric() -> None:
    report = model_result_to_report(model_result(), metric="accuracy")
    assert report["metric"] == "accuracy"
    assert report["score"] == pytest.approx(0.875)


def test_model_result_to_report_rejects_missing_metric() -> None:
    with pytest.raises(ModelReportingError):
        model_result_to_report(model_result(), metric="missing")


def test_model_result_to_report_rejects_missing_split() -> None:
    with pytest.raises(ModelReportingError):
        model_result_to_report(model_result(), split="validation")
