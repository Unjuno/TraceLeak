from pathlib import Path

from examples.synthetic.target import make_run, write_jsonl
from traceleak.workflow import run_lightweight_experiment


def test_synthetic_generated_e2e(tmp_path) -> None:
    trace_path = tmp_path / "generated_synthetic.jsonl"
    runs = [make_run(index, leak=True) for index in range(4)]
    write_jsonl(trace_path, runs)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "experiment_id": "tmp_synthetic_generated",
  "experiment_type": "synthetic",
  "target": "synthetic-leak",
  "view": "redacted",
  "metric": "DeltaH",
  "inputs": {
    "trace": "generated_synthetic.jsonl",
    "ablation": "ablation.json",
    "baseline": "baseline.json"
  },
  "safety": {
    "contains_raw_trace": false,
    "contains_secret_equivalent": false,
    "public_safe": true
  }
}
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "ablation.json").write_text(
        """
{
  "target": "synthetic-leak",
  "view": "redacted",
  "metric": "DeltaH",
  "full_score": 4.0,
  "groups": {
    "synthetic_branch_event": {
      "ablated_score": 1.0,
      "group_type": "branch",
      "location": "examples/synthetic/target.py:19"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "baseline.json").write_text(
        """
{
  "target": "synthetic-leak",
  "view": "redacted",
  "label_name": "synthetic_bucket",
  "examples": [
    {"run_id": "r1", "label": "A", "features": {"phase=alpha": 1.0}},
    {"run_id": "r2", "label": "A", "features": {"phase=alpha": 1.0}},
    {"run_id": "r3", "label": "B", "features": {"phase=beta": 1.0}},
    {"run_id": "r4", "label": "B", "features": {"phase=beta": 1.0}}
  ]
}
""".strip(),
        encoding="utf-8",
    )

    result = run_lightweight_experiment(config_path, out_dir=tmp_path / "out", root=tmp_path)
    names = {path.name for path in result.written_paths}
    assert "tmp_synthetic_generated.features.json" in names
    assert "tmp_synthetic_generated.features.csv" in names
    assert "tmp_synthetic_generated.baseline.json" in names
    assert "tmp_synthetic_generated.md" in names
    assert "tmp_synthetic_generated.json" in names
