import pytest

from traceleak.review_flow import REVIEW_FLOW_STEPS, ReviewFlowError, build_review_flow, validate_review_flow


def test_build_review_flow_is_review_only_p3_contract() -> None:
    flow = build_review_flow()

    assert flow["format"] == "traceleak.review_flow.v1"
    assert flow["status"] == "ready"
    assert flow["mode"] == "review_only"
    assert flow["stage"] == "P3"
    assert flow["steps"] == REVIEW_FLOW_STEPS
    assert flow["template_state"] == "pending"
    assert flow["record_state"] == "human_edited"
    assert flow["auto_approval"] is False


def test_review_flow_rejects_auto_approval() -> None:
    flow = build_review_flow()
    flow["auto_approval"] = True

    with pytest.raises(ReviewFlowError, match="auto_approval"):
        validate_review_flow(flow)


def test_review_flow_rejects_missing_step() -> None:
    flow = build_review_flow()
    flow["steps"] = ["verify_local"]

    with pytest.raises(ReviewFlowError, match="steps missing"):
        validate_review_flow(flow)
