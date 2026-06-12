import pytest

from traceleak.review_chain_snapshot import (
    ReviewChainSnapshotError,
    build_review_chain_snapshot,
    validate_review_chain_snapshot,
)


def test_build_review_chain_snapshot_contains_complete_p3_p5_chain() -> None:
    snapshot = build_review_chain_snapshot()

    assert snapshot["format"] == "traceleak.review_chain_snapshot.v1"
    assert snapshot["mode"] == "review_only"
    assert snapshot["activation_allowed"] is False
    assert snapshot["auto_approval"] is False
    assert snapshot["review_flow"]["stage"] == "P3"
    assert snapshot["artifact_slot_set"]["stage"] == "P4"
    assert snapshot["p5_contract"]["stage"] == "P5"
    assert snapshot["chain_contract"]["chain"] == ["P3", "P4", "P5"]


def test_review_chain_snapshot_rejects_activation_allowed() -> None:
    snapshot = build_review_chain_snapshot()
    snapshot["activation_allowed"] = True

    with pytest.raises(ReviewChainSnapshotError, match="activation_allowed"):
        validate_review_chain_snapshot(snapshot)


def test_review_chain_snapshot_rejects_nested_auto_approval() -> None:
    snapshot = build_review_chain_snapshot()
    snapshot["p5_contract"]["auto_approval"] = True

    with pytest.raises(ValueError, match="auto_approval"):
        validate_review_chain_snapshot(snapshot)
