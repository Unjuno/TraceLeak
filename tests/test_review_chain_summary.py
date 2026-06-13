import pytest

from traceleak.review_chain_snapshot import build_review_chain_snapshot
from traceleak.review_chain_summary import (
    ReviewChainSummaryError,
    build_review_chain_summary,
    validate_review_chain_summary,
)


def test_build_review_chain_summary_compacts_snapshot() -> None:
    summary = build_review_chain_summary(snapshot=build_review_chain_snapshot())

    assert summary["format"] == "traceleak.review_chain_summary.v1"
    assert summary["mode"] == "review_only"
    assert summary["chain"] == ["P3", "P4", "P5"]
    assert summary["artifact_slot_count"] == len(summary["artifact_kinds"])
    assert summary["artifact_slot_count"] > 0
    assert summary["p5_requirements"]
    assert summary["activation_allowed"] is False
    assert summary["auto_approval"] is False


def test_review_chain_summary_rejects_activation_allowed() -> None:
    summary = build_review_chain_summary(snapshot=build_review_chain_snapshot())
    summary["activation_allowed"] = True

    with pytest.raises(ReviewChainSummaryError, match="activation_allowed"):
        validate_review_chain_summary(summary)


def test_review_chain_summary_rejects_empty_artifacts() -> None:
    summary = build_review_chain_summary(snapshot=build_review_chain_snapshot())
    summary["artifact_kinds"] = []

    with pytest.raises(ReviewChainSummaryError, match="artifact_kinds"):
        validate_review_chain_summary(summary)
