import pytest

from traceleak.baselines import (
    BaselineError,
    LabeledFeatureVector,
    jaccard_similarity,
    label_distribution,
    leave_one_out_majority_accuracy,
    leave_one_out_nearest_neighbor_accuracy,
    majority_label,
    majority_predictions,
    nearest_neighbor_predict_one,
    nonzero_feature_set,
)


def examples() -> list[LabeledFeatureVector]:
    return [
        LabeledFeatureVector(label="A", features={"phase=alpha": 1.0, "event_type=branch": 1.0}),
        LabeledFeatureVector(label="A", features={"phase=alpha": 1.0, "event_type=branch": 1.0}),
        LabeledFeatureVector(label="B", features={"phase=beta": 1.0, "event_type=loop": 1.0}),
        LabeledFeatureVector(label="B", features={"phase=beta": 1.0, "event_type=loop": 1.0}),
    ]


def test_majority_label_tie_breaks_deterministically() -> None:
    assert majority_label(["B", "A"]) == "A"


def test_majority_predictions() -> None:
    assert majority_predictions(["A", "A", "B"], 3) == ["A", "A", "A"]


def test_nonzero_feature_set() -> None:
    assert nonzero_feature_set({"a": 1.0, "b": 0.0}) == {"a"}


def test_jaccard_similarity() -> None:
    assert jaccard_similarity({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)
    assert jaccard_similarity(set(), set()) == pytest.approx(1.0)


def test_nearest_neighbor_predict_one() -> None:
    query = LabeledFeatureVector(label="?", features={"phase=alpha": 1.0})
    assert nearest_neighbor_predict_one(examples(), query) == "A"


def test_leave_one_out_majority_accuracy() -> None:
    assert leave_one_out_majority_accuracy(examples()) == pytest.approx(0.0)


def test_leave_one_out_nearest_neighbor_accuracy() -> None:
    assert leave_one_out_nearest_neighbor_accuracy(examples()) == pytest.approx(1.0)


def test_label_distribution() -> None:
    assert label_distribution(examples()) == {"A": 2, "B": 2}


def test_baselines_reject_small_inputs() -> None:
    with pytest.raises(BaselineError):
        leave_one_out_majority_accuracy([])
    with pytest.raises(BaselineError):
        leave_one_out_nearest_neighbor_accuracy([examples()[0]])
    with pytest.raises(BaselineError):
        majority_label([])
