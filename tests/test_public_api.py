from pathlib import Path

import traceleak
from traceleak import (
    AttributionScore,
    TraceEvent,
    TraceRun,
    WorkflowResult,
    ablation_drop,
    accuracy,
    classify_delta,
    delta_h,
    extract_feature_vector,
    patch_verification_report_dict,
    run_lightweight_experiment,
    stability_result,
    stability_summary,
    to_view,
    top_k_recall,
    validate_config,
    validate_patch_verification,
    validate_run,
    verification_delta,
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


def sample_patch_verification() -> dict:
    return {
        "verification_id": "api_patch_0001",
        "target": "synthetic-example",
        "view": "redacted",
        "metric": "DeltaH",
        "before": {"run_id": "before", "score": 4.0},
        "after": {"run_id": "after", "score": 1.0},
        "delta": 3.0,
        "status": "reduced",
    }


def sample_stability_input() -> dict:
    return {
        "stability_id": "api_stability_0001",
        "target": "synthetic-example",
        "view": "redacted",
        "metric": "DeltaH",
        "before_scores": [4.0, 4.1, 3.9],
        "after_scores": [1.0, 1.1, 0.9],
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
    assert isinstance(TraceRun(run_id="r", target="t", target_version="v", view="meta", events=[]), TraceRun)

    path_view = to_view(run, "path")
    assert path_view["view"] == "path"
    assert extract_feature_vector(run)["run.view=redacted"] == 1.0


def test_public_api_patch_verification_functions() -> None:
    result = sample_patch_verification()
    validate_patch_verification(result)
    assert verification_delta(4.0, 1.0) == 3.0
    assert classify_delta(3.0) == "reduced"
    report = patch_verification_report_dict(result)
    assert report["report_type"] == "patch_verification"
    assert report["status"] == "reduced"


def test_public_api_stability_functions() -> None:
    summary = stability_summary([4.0, 4.1, 3.9], [1.0, 1.1, 0.9])
    assert summary["status"] == "reduced"
    result = stability_result(sample_stability_input())
    assert result["result_type"] == "repeated_run_stability"
    assert result["summary"]["status"] == "reduced"


def test_public_api_workflow_result_type() -> None:
    result = WorkflowResult("exp", (Path("a"),))
    assert result.experiment_id == "exp"
    assert result.written_paths == (Path("a"),)
    assert callable(run_lightweight_experiment)
