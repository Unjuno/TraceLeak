import pytest

from traceleak.stage_plan import STAGES, StagePlanError, build_stage_plan, validate_stage_plan


def test_build_stage_plan() -> None:
    plan = build_stage_plan()

    assert plan["format"] == "traceleak.stage_plan.v1"
    assert plan["mode"] == "review_only"
    assert plan["stages"] == STAGES
    assert plan["activation"]["P3"] == "notes_only"
    assert plan["activation"]["P4"] == "planning_only"
    assert plan["activation"]["P5"] == "design_only"


def test_validate_stage_plan_rejects_bad_p5() -> None:
    plan = build_stage_plan()
    plan["activation"]["P5"] = "enabled"

    with pytest.raises(StagePlanError, match="activation.P5"):
        validate_stage_plan(plan)
