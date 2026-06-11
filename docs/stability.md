# Repeated-Run Stability

Repeated-run stability checks summarize whether a before/after signal reduction is directionally stable across multiple local runs.

This is a public-safe summary workflow. Inputs are score lists, not raw traces.

## Purpose

```text
before repeated scores
  -> after repeated scores
  -> evaluate_stability.py
  -> repeated-run stability result
```

A single before/after comparison can support a weak local observation. Repeated-run stability is stronger evidence because it checks whether the mean direction persists relative to observed variance.

## Example Input

```json
{
  "stability_id": "synthetic_stability_0001",
  "target": "synthetic-leak",
  "view": "redacted",
  "metric": "DeltaH",
  "before_scores": [4.2, 4.0, 4.1, 3.9, 4.05],
  "after_scores": [1.1, 1.0, 1.2, 0.95, 1.05]
}
```

## Evaluate

```bash
python scripts/evaluate_stability.py examples/synthetic/stability_sample.json
```

Write result JSON:

```bash
python scripts/evaluate_stability.py examples/synthetic/stability_sample.json --out stability_result.json
```

## Output Fields

| Field | Meaning |
|---|---|
| `before_mean` | Mean before-patch score |
| `after_mean` | Mean after-patch score |
| `before_stdev` | Sample standard deviation before patch |
| `after_stdev` | Sample standard deviation after patch |
| `pooled_stdev` | Pooled standard deviation |
| `mean_delta` | `before_mean - after_mean` |
| `relative_delta` | `mean_delta / before_mean`, when defined |
| `margin` | Absolute mean delta divided by pooled standard deviation |
| `direction` | Direction from mean delta |
| `status` | Directional stability status |

## Status Values

| Status | Meaning |
|---|---|
| `reduced` | Mean score decreased and margin threshold passed |
| `unchanged` | Mean delta stayed within tolerance |
| `increased` | Mean score increased and margin threshold passed |
| `inconclusive` | Direction exists but margin threshold did not pass |

## Public-Safe Rule

Stability inputs must not contain raw traces, private values, random generator state, or secret-equivalent fields.
