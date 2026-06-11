import pytest

from traceleak.attribution import (
    AttributionError,
    ablation_drop,
    make_ablation_scores,
    rank_attributions,
)


def test_ablation_drop() -> None:
    assert ablation_drop(8.0, 3.0) == pytest.approx(5.0)


def test_ablation_drop_allows_negative_noise() -> None:
    assert ablation_drop(3.0, 4.0) == pytest.approx(-1.0)


def test_ablation_drop_rejects_negative_scores() -> None:
    with pytest.raises(AttributionError):
        ablation_drop(-1.0, 0.0)
    with pytest.raises(AttributionError):
        ablation_drop(1.0, -1.0)


def test_make_ablation_scores_ranks_by_contribution() -> None:
    scores = make_ablation_scores(
        full_score=10.0,
        ablated_scores={"loop_count": 7.0, "branch": 2.0},
        group_type="variable",
        locations={"branch": "target.c:21"},
    )
    assert [score.group_id for score in scores] == ["branch", "loop_count"]
    assert scores[0].contribution == pytest.approx(8.0)
    assert scores[0].location == "target.c:21"


def test_make_ablation_scores_rejects_empty_input() -> None:
    with pytest.raises(AttributionError):
        make_ablation_scores(full_score=1.0, ablated_scores={}, group_type="variable")


def test_rank_attributions_is_deterministic() -> None:
    scores = make_ablation_scores(
        full_score=10.0,
        ablated_scores={"b": 8.0, "a": 8.0},
        group_type="variable",
    )
    ranked = rank_attributions(scores)
    assert [score.group_id for score in ranked] == ["b", "a"]
