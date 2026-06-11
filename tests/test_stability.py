import math

import pytest

from traceleak.stability import (
    StabilityError,
    mean,
    pooled_stdev,
    sample_stdev,
    sample_variance,
    stability_result,
    stability_summary,
    validate_stability_input,
)


def valid_input() -> dict:
    return {
        "stability_id": "synthetic_stability_0001",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "before_scores": [4.2, 4.0, 4.1, 3.9, 4.05],
        "after_scores": [1.1, 1.0, 1.2, 0.95, 1.05],
    }


def test_basic_statistics() -> None:
    assert mean([1.0, 2.0, 3.0]) == pytest.approx(2.0)
    assert sample_variance([1.0, 2.0, 3.0]) == pytest.approx(1.0)
    assert sample_stdev([1.0, 2.0, 3.0]) == pytest.approx(1.0)
    assert pooled_stdev([1.0, 2.0], [3.0, 4.0]) == pytest.approx(math.sqrt(0.5))


def test_stability_summary_reduced() -> None:
    summary = stability_summary([4.0, 4.1, 3.9], [1.0, 1.1, 0.9])
    assert summary["direction"] == "reduced"
    assert summary["status"] == "reduced"
    assert summary["mean_delta"] == pytest.approx(3.0)
    assert summary["margin"] > 1.0


def test_stability_summary_inconclusive_when_margin_is_low() -> None:
    summary = stability_summary([4.0, 8.0], [3.9, 7.9], min_margin=1.0)
    assert summary["direction"] == "reduced"
    assert summary["status"] == "inconclusive"


def test_stability_summary_unchanged() -> None:
    summary = stability_summary([1.0, 1.0], [1.0, 1.0])
    assert summary["direction"] == "unchanged"
    assert summary["status"] == "unchanged"


def test_validate_stability_input_accepts_valid_input() -> None:
    validate_stability_input(valid_input())


def test_validate_stability_input_rejects_raw_public_view() -> None:
    data = valid_input()
    data["view"] = "raw"
    with pytest.raises(StabilityError):
        validate_stability_input(data)


def test_validate_stability_input_rejects_secret_equivalent_field() -> None:
    data = valid_input()
    data["value_raw"] = "not allowed"
    with pytest.raises(StabilityError):
        validate_stability_input(data)


def test_stability_result() -> None:
    result = stability_result(valid_input())
    assert result["result_type"] == "repeated_run_stability"
    assert result["stability_id"] == "synthetic_stability_0001"
    assert result["summary"]["status"] == "reduced"
