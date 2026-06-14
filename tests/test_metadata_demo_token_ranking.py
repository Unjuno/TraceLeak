import pytest

from traceleak.metadata_demo_token_ranking import (
    MetadataDemoTokenRankingError,
    build_metadata_demo_token_ranking,
    validate_metadata_demo_token_ranking,
)


def test_metadata_demo_token_ranking_builds_from_demo_outputs(metadata_demo_artifacts) -> None:
    ranking = build_metadata_demo_token_ranking(
        demo_manifest=metadata_demo_artifacts["demo_manifest"],
        nn_result=metadata_demo_artifacts["nn_result"],
    )

    assert ranking["format"] == "traceleak.metadata_demo_token_ranking.v1"
    assert ranking["phase"] == "P30"
    assert ranking["mode"] == "metadata_only_ranking"
    assert ranking["sample_digest"] == metadata_demo_artifacts["demo_manifest"]["sample_digest"]
    assert ranking["public_status"]["metadata_only"] is True
    assert ranking["public_status"]["payload_free"] is True
    assert ranking["public_status"]["public_safe"] is True
    assert ranking["public_status"]["real_world_claim"] is False


def test_metadata_demo_token_ranking_rejects_non_numeric_score(metadata_demo_artifacts) -> None:
    ranking = build_metadata_demo_token_ranking(
        demo_manifest=metadata_demo_artifacts["demo_manifest"],
        nn_result=metadata_demo_artifacts["nn_result"],
    )
    if ranking["ranked_tokens"]:
        ranking["ranked_tokens"][0]["score"] = "bad"
    else:
        ranking["ranked_tokens"].append({"group_id": "x", "score": "bad"})
        ranking["ranked_token_count"] = 1

    with pytest.raises(MetadataDemoTokenRankingError, match="score"):
        validate_metadata_demo_token_ranking(ranking)


def test_metadata_demo_token_ranking_rejects_real_world_claim(metadata_demo_artifacts) -> None:
    ranking = build_metadata_demo_token_ranking(
        demo_manifest=metadata_demo_artifacts["demo_manifest"],
        nn_result=metadata_demo_artifacts["nn_result"],
    )
    ranking["public_status"]["real_world_claim"] = True

    with pytest.raises(MetadataDemoTokenRankingError, match="real_world_claim"):
        validate_metadata_demo_token_ranking(ranking)
