# Negative Controls

Negative controls help prevent over-claiming. In TraceLeak, a negative control is a public-safe comparison where a change should not reduce the measured signal.

Typical examples:

- a noop patch;
- a formatting-only source change;
- a control condition without the synthetic leak trigger;
- a measurement rerun expected to remain unchanged.

## Purpose

```text
before noop/control condition
  -> after noop/control condition
  -> comparison_to_report.py
  -> unchanged or inconclusive result
```

A negative control should not produce an apparent patch success claim. If a negative control reports a strong reduction, the experiment design or measurement pipeline needs review.

## Example

```json
{
  "comparison_id": "synthetic_negative_control_0001",
  "comparison_type": "negative_control",
  "target": "synthetic-leak",
  "view": "redacted",
  "metric": "DeltaH",
  "left": {
    "label": "before_noop_patch",
    "score": 4.0
  },
  "right": {
    "label": "after_noop_patch",
    "score": 4.0
  },
  "delta": 0.0,
  "status": "unchanged"
}
```

## Render

```bash
python scripts/comparison_to_report.py --in examples/synthetic/negative_control_sample.json --out negative_control_report.md
```

JSON report:

```bash
python scripts/comparison_to_report.py --in examples/synthetic/negative_control_sample.json --out negative_control_report.json --format json
```

## Expected Interpretation

| Status | Interpretation |
|---|---|
| `unchanged` | Negative control behaved as expected |
| `inconclusive` | Result is not strong enough to interpret |
| `higher` or `lower` | Review the measurement design before making a patch claim |

## Safety Boundary

Negative control files follow the same public-safe boundary as comparison files. They may include labels, report paths, and derived scores. They must not include raw traces, private keys, RNG state, or secret-equivalent values.
