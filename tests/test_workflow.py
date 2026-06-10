import json
from pathlib import Path

import pytest

from traceleak.workflow import WorkflowError, load_public_runs, run_lightweight_experiment


def test_run_lightweight_experiment_api(tmp_path) -> None:
    result = run_lightweight_experiment(
        "experiments/exp_000_synthetic_leak/config.json",
        out_dir=tmp_path,
    )

    assert result.experiment_id == "exp_000_synthetic_leak"
    assert len(result.written_paths) == 5

    generated = {path.name for path in result.written_paths}
    assert "exp_000_synthetic_leak.features.json" in generated
    assert "exp_000_synthetic_leak.features.csv" in generated
    assert "exp_000_synthetic_leak.baseline.json" in generated

    # The sample config has explicit report paths under reports/local.
    assert Path("reports/local/exp_000_synthetic_leak.md") in result.written_paths
    assert Path("reports/local/exp_000_synthetic_leak.json") in result.written_paths

    report = json.loads(Path("reports/local/exp_000_synthetic_leak.json").read_text(encoding="utf-8"))
    assert report["target"] == "synthetic-example"

    for path in [
        Path("reports/local/exp_000_synthetic_leak.md"),
        Path("reports/local/exp_000_synthetic_leak.json"),
    ]:
        path.unlink(missing_ok=True)


def test_load_public_runs_rejects_empty_file(tmp_path) -> None:
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")
    with pytest.raises(WorkflowError):
        load_public_runs(path)
