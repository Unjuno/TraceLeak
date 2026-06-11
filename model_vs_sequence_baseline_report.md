# TraceLeak Comparison Report

- Comparison ID: `synthetic_model_vs_sequence_baseline_0001`
- Type: `model_vs_sequence_baseline`
- Target: `synthetic-leak`
- View: `redacted`
- Metric: `accuracy`
- Status: `lower`
- Delta: `-0.125`

## Measurements

| Side | Label | Score | Report |
|---|---|---:|---|
| `left` | `local-neural-placeholder` | 0.875 | `examples/synthetic/model_result_sample.json` |
| `right` | `sequence_nearest_neighbor_baseline` | 1 | `examples/synthetic/model_sequence_baseline_result_sample.json` |

## Interpretation

The placeholder model result is lower than the sequence nearest-neighbor baseline in this synthetic public-safe sample. This is a sanity check showing that variable/control-flow sequence baselines must be compared before making neural-model claims.

## Notes

- Public-safe comparison between a model result sample and a model-sequence baseline sample.
- This is not a neural training result; the model side is a placeholder imported result.
