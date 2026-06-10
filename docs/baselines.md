# Baseline Evaluation

TraceLeak includes lightweight baselines for sanity checks before local neural-network training.

These baselines do not use scikit-learn, NumPy, PyTorch, or TensorFlow. They are intentionally simple and dependency-free.

## Purpose

Before training a heavier model, check whether simple baselines already explain the labels.

```text
feature vectors + lab-only labels
  -> majority baseline
  -> nearest-neighbor baseline
  -> sanity-check report
  -> local NN training, if still useful
```

If a trivial baseline performs strongly, a neural model may not be necessary for the initial claim.

If a neural model performs strongly but all simple baselines fail, the result may be more interesting but also requires stronger validation.

## Included Baselines

| Baseline | Description |
|---|---|
| majority | Always predicts the most frequent training label |
| sparse nearest neighbor | Uses Jaccard similarity over non-zero feature names |

Both default evaluations use leave-one-out splitting.

## Input Format

```json
{
  "target": "synthetic-example",
  "view": "redacted",
  "label_name": "synthetic_bucket",
  "examples": [
    {
      "run_id": "synthetic_000001",
      "label": "A",
      "features": {
        "event_type=branch": 1.0,
        "phase=alpha": 1.0
      }
    }
  ]
}
```

## Run Baseline Evaluation

```bash
python scripts/evaluate_baseline.py --in examples/synthetic/baseline_sample.json
```

PowerShell:

```powershell
python scripts/evaluate_baseline.py --in examples/synthetic/baseline_sample.json
```

Write JSON output:

```bash
python scripts/evaluate_baseline.py \
  --in examples/synthetic/baseline_sample.json \
  --out baseline_result.json
```

PowerShell:

```powershell
python scripts/evaluate_baseline.py --in examples/synthetic/baseline_sample.json --out baseline_result.json
```

## Output Format

```json
{
  "target": "synthetic-example",
  "view": "redacted",
  "label_name": "synthetic_bucket",
  "example_count": 4,
  "label_distribution": {
    "A": 2,
    "B": 2
  },
  "baselines": {
    "leave_one_out_majority_accuracy": 0.0,
    "leave_one_out_nearest_neighbor_accuracy": 1.0
  }
}
```

## Interpretation

Baseline results are not security claims by themselves.

They are used to check whether trace labels can already be predicted by simple feature structure.

Useful checks:

- metadata-only baseline should usually be weak;
- path-only baseline may reveal execution-path signal;
- redacted baseline may reveal value-derived signal;
- nearest-neighbor strength may indicate feature clustering rather than generalizable leakage;
- local NN results should be compared against these baselines.

## Local Output Policy

Baseline output files generated at repo root should be treated as local experiment artifacts unless intentionally moved under `examples/`.
