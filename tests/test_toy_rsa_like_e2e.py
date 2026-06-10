from examples.toy_rsa_like.target import make_run, write_jsonl
from traceleak.workflow import run_lightweight_experiment


def test_toy_rsa_like_e2e(tmp_path) -> None:
    trace_path = tmp_path / "toy_rsa_like.jsonl"
    runs = [make_run(index) for index in range(6)]
    write_jsonl(trace_path, runs)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "experiment_id": "tmp_toy_rsa_like",
  "experiment_type": "toy-rsa",
  "target": "toy-rsa-like",
  "view": "redacted",
  "metric": "DeltaH",
  "inputs": {
    "trace": "toy_rsa_like.jsonl",
    "ablation": "toy_ablation.json",
    "baseline": "toy_baseline.json"
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
    (tmp_path / "toy_ablation.json").write_text(
        """
{
  "target": "toy-rsa-like",
  "view": "redacted",
  "metric": "DeltaH",
  "full_score": 6.0,
  "groups": {
    "candidate_result": {
      "ablated_score": 2.0,
      "group_type": "branch",
      "location": "examples/toy_rsa_like/target.py:35"
    }
  }
}
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "toy_baseline.json").write_text(
        """
{
  "target": "toy-rsa-like",
  "view": "redacted",
  "label_name": "toy_result_bucket",
  "examples": [
    {"run_id": "r1", "label": "accepted", "features": {"phase=result": 1.0}},
    {"run_id": "r2", "label": "accepted", "features": {"phase=result": 1.0}},
    {"run_id": "r3", "label": "small_divisor", "features": {"phase=filter": 1.0}},
    {"run_id": "r4", "label": "small_divisor", "features": {"phase=filter": 1.0}}
  ]
}
""".strip(),
        encoding="utf-8",
    )

    result = run_lightweight_experiment(config_path, out_dir=tmp_path / "out", root=tmp_path)
    names = {path.name for path in result.written_paths}
    assert "tmp_toy_rsa_like.features.json" in names
    assert "tmp_toy_rsa_like.features.csv" in names
    assert "tmp_toy_rsa_like.baseline.json" in names
    assert "tmp_toy_rsa_like.md" in names
    assert "tmp_toy_rsa_like.json" in names
