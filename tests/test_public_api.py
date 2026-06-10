from pathlib import Path

import traceleak
from traceleak import (
    AttributionScore,
    TraceEvent,
    TraceRun,
    WorkflowResult,
    ablation_drop,
    accuracy,
    delta_h,
    extract_feature_vector,
    run_lightweight_experiment,
    to_view,
    top_k_recall,
    validate_config,
    validate_run,
)


def sample_run() -> dict:
    return {
        "run_id": "api_000001",
        "target": "synthetic-example",
        "target_version": "v0",
        "view": "redacted",
        "events": [
            {
                "step": 1,
                "phase": "api_phase",
                "function": "api_fn",
                "event_type": "branch",
                "name": "api_branch_event",
                "value_redacted": {"count": 1},
            }
        ],
    }


def test_public_api_exports_expected_names() -> None:
    for name in traceleak.__all__:
        assert hasattr(traceleak, name)


def test_public_api_core_functions() -> None:
    run = sample_run()
    validate_run(run)
    validate_config(
        {
            "experiment_id": "api_exp",
            "experiment_type": "synthetic",
            "target": "synthetic-example",
            "view": "redacted",
            "metric": "DeltaH",
            "inputs": {"trace": "example.jsonl"},
        }
    )

    assert delta_h(16, 4) == 2.0
    assert accuracy(["a", "b"], ["a", "x"]) == 0.5
    assert top_k_recall(["a"], [["x", "a"]]) == 1.0
    assert ablation_drop(5.0, 2.0) == 3.0
    assert isinstance(AttributionScore(1.0, "g", "branch"), AttributionScore)
    assert isinstance(TraceEvent(step=1, phase="p", function="f", event_type="phase", name="n"), TraceEvent)
    assert isinstance(TraceRun(run_id="r", target="t", target_version="v", view="meta"), TraceRun)

    path_view = to_view(run, "path")
    assert path_view["view"] == "path"
    assert extract_feature_vector(run)["run.view=redacted"] == 1.0


def test_public_api_workflow_result_type() -> None:
    result = WorkflowResult("exp", (Path("a"),))
    assert result.experiment_id == "exp"
    assert result.written_paths == (Path("a"),)
    assert callable(run_lightweight_experiment)
