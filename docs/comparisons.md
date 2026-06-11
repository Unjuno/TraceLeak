# Comparison Reports

Comparison reports summarize two public-safe measurements in a common format.

Typical uses:

- leak condition versus control condition;
- model result versus baseline result;
- synthetic result versus toy target result.

The comparison input must contain public-safe scores only. It must not contain raw traces or secret-equivalent values.

## Example

```json
{
  "comparison_id": "synthetic_leak_control_0001",
  "comparison_type": "leak_vs_control",
  "target": "synthetic-leak",
  "view": "redacted",
  "metric": "DeltaH",
  "left": {
    "label": "leak",
    "score": 4.0,
    "report": "reports/local/synthetic_leak.md"
  },
  "right": {
    "label": "control",
    "score": 0.2,
    "report": "reports/local/synthetic_control.md"
  },
  "delta": 3.8,
  "status": "higher"
}
```

## Render

Markdown report:

```bash
python scripts/comparison_to_report.py --in examples/synthetic/comparison_sample.json --out comparison_report.md
```

JSON report:

```bash
python scripts/comparison_to_report.py --in examples/synthetic/comparison_sample.json --out comparison_report.json --format json
```

## Status Values

| Status | Meaning |
|---|---|
| `higher` | Left score is higher than right score |
| `lower` | Left score is lower than right score |
| `unchanged` | Difference is within tolerance |
| `inconclusive` | Direction is not strong enough to claim |

## Public-Safe Boundary

Comparison files may include:

- public-safe report paths;
- labels;
- derived scores;
- comparison type;
- status;
- notes.

Comparison files must not include:

- raw traces;
- private keys;
- random generator state;
- raw candidate values;
- secret-equivalent fields.
