import math

import pytest

from traceleak.attribution import (
    AttributionError,
    ablation_drop,
    make_ablation_scores,
    rank_attributions,
)
from traceleak.attribution_export_schema import (
    ATTRIBUTION_EXPORT_FORMAT,
    AttributionExportRecord,
    AttributionExportSchemaError,
    attribution_export_record,
    attribution_export_record_from_dict,
    sort_attribution_export_records,
    validate_attribution_export_record,
    validate_attribution_export_records,
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


def sample_export_record() -> dict:
    return {
        "sample_id": "sample_000001",
        "model_id": "transformer_baseline_000001",
        "model_family": "transformer",
        "attribution_level": "graph_edge",
        "entity_id": "edge:reads:evt_000001:var:op",
        "entity_type": "graph_edge",
        "score": 0.75,
        "score_semantics": "attention_pattern",
        "rank": 1,
        "method": "attention_weight",
        "evidence": {
            "summary": "attention mass assigned to this edge",
            "claim_scope": "attention_pattern_only",
        },
        "metadata": {
            "public_safe": True,
            "layer": 2,
            "head": 1,
        },
    }


def test_attribution_export_record_accepts_full_record() -> None:
    record = sample_export_record()
    validate_attribution_export_record(record)
    parsed = attribution_export_record_from_dict(record)
    assert isinstance(parsed, AttributionExportRecord)
    assert parsed.to_dict() == record
    assert ATTRIBUTION_EXPORT_FORMAT == "traceleak.attention_attribution_export.v1"


def test_attribution_export_record_rejects_missing_field() -> None:
    record = sample_export_record()
    del record["entity_id"]
    with pytest.raises(AttributionExportSchemaError, match="missing required"):
        validate_attribution_export_record(record)


def test_attribution_export_record_rejects_level_type_mismatch() -> None:
    record = sample_export_record()
    record["entity_type"] = "token"
    with pytest.raises(AttributionExportSchemaError, match="entity_type must match"):
        validate_attribution_export_record(record)


def test_attribution_export_record_rejects_non_finite_score() -> None:
    record = sample_export_record()
    record["score"] = math.inf
    with pytest.raises(AttributionExportSchemaError, match="finite number"):
        validate_attribution_export_record(record)


def test_attention_method_requires_attention_semantics() -> None:
    record = sample_export_record()
    record["score_semantics"] = "local_ablation_effect"
    with pytest.raises(AttributionExportSchemaError, match="requires score_semantics"):
        validate_attribution_export_record(record)


def test_attribution_export_records_reject_duplicate_keys() -> None:
    first = sample_export_record()
    second = sample_export_record()
    with pytest.raises(AttributionExportSchemaError, match="duplicate"):
        validate_attribution_export_records([first, second])


def test_attribution_export_sort_is_deterministic() -> None:
    first = sample_export_record()
    second = attribution_export_record(
        sample_id="sample_000001",
        model_id="transformer_baseline_000001",
        model_family="transformer",
        attribution_level="token",
        entity_id="token:event_type:branch",
        score=0.2,
        rank=2,
        method="attention_weight",
        evidence_summary="token attention pattern",
    )
    sorted_records = sort_attribution_export_records([first, second])
    assert [record["attribution_level"] for record in sorted_records] == [
        "graph_edge",
        "token",
    ]


def test_attribution_export_builder_sets_method_semantics() -> None:
    record = attribution_export_record(
        sample_id="sample_000001",
        model_id="ablation_baseline_000001",
        model_family="hybrid",
        attribution_level="event",
        entity_id="evt_000001",
        score=0.31,
        rank=1,
        method="ablation_drop",
        evidence_summary="drop after masking event",
        metadata={"mask_type": "event"},
    )
    validate_attribution_export_record(record)
    assert record["score_semantics"] == "local_ablation_effect"
    assert record["evidence"]["claim_scope"] == "local_model_explanation"
