import pytest

from traceleak.review_artifact_manifest import REVIEW_ARTIFACT_KINDS, build_review_artifact_manifest
from traceleak.review_artifact_slot_set import (
    ReviewArtifactSlotSetError,
    build_review_artifact_slot_set,
    validate_review_artifact_slot_set,
)
from traceleak.review_flow import build_review_flow
from traceleak.review_flow_artifact_link import build_review_flow_artifact_link
from traceleak.stage_plan import build_stage_plan


def make_slot_set() -> dict:
    manifest = build_review_artifact_manifest(stage_plan=build_stage_plan())
    link = build_review_flow_artifact_link(
        review_flow=build_review_flow(),
        artifact_manifest=manifest,
    )
    return build_review_artifact_slot_set(
        artifact_manifest=manifest,
        flow_artifact_link=link,
    )


def test_build_review_artifact_slot_set_creates_empty_review_slots() -> None:
    slot_set = make_slot_set()

    assert slot_set["format"] == "traceleak.review_artifact_slot_set.v1"
    assert slot_set["mode"] == "review_only"
    assert slot_set["stage"] == "P4"
    assert slot_set["stage_mode"] == "planning_only"
    assert slot_set["auto_approval"] is False
    assert [slot["kind"] for slot in slot_set["slots"]] == REVIEW_ARTIFACT_KINDS
    assert {slot["content_state"] for slot in slot_set["slots"]} == {"empty"}
    assert {slot["review_required"] for slot in slot_set["slots"]} == {True}


def test_review_artifact_slot_set_rejects_filled_content_state() -> None:
    slot_set = make_slot_set()
    slot_set["slots"][0]["content_state"] = "filled"

    with pytest.raises(ReviewArtifactSlotSetError, match="content_state"):
        validate_review_artifact_slot_set(slot_set)


def test_review_artifact_slot_set_rejects_auto_approval() -> None:
    slot_set = make_slot_set()
    slot_set["auto_approval"] = True

    with pytest.raises(ReviewArtifactSlotSetError, match="auto_approval"):
        validate_review_artifact_slot_set(slot_set)
