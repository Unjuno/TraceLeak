import math

import pytest

from traceleak.metrics import MetricError, accuracy, delta_h, top_k_recall


def test_delta_h() -> None:
    assert delta_h(1024, 64) == pytest.approx(4.0)


def test_delta_h_rejects_invalid_counts() -> None:
    with pytest.raises(MetricError):
        delta_h(0, 1)
    with pytest.raises(MetricError):
        delta_h(8, 0)
    with pytest.raises(MetricError):
        delta_h(8, 16)


def test_accuracy() -> None:
    assert accuracy([1, 2, 3], [1, 0, 3]) == pytest.approx(2 / 3)


def test_top_k_recall() -> None:
    assert top_k_recall(["a", "b", "c"], [["a"], ["x", "b"], ["z"]]) == pytest.approx(2 / 3)


def test_metric_outputs_are_finite() -> None:
    assert math.isfinite(delta_h(16, 1))
