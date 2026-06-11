# Patch Verification

Patch verification records whether a candidate source change reduced a measured TraceLeak signal.

It is a public-safe summary format. It must not contain raw traces, private values, random generator state, or secret-equivalent material.

## Purpose

```text
before report
  -> source change
  -> after report
  -> patch verification JSON
  -> validate_patch_verification.py
```

Patch verification is the path toward stronger TraceLeak claims. A single before/after comparison is not enough for a production security claim, but it is useful evidence for local controlled experiments.

## Example

```json
{
  "verification_id": "synthetic_patch_0001",
  "target": "synthetic-leak",
  "view": "redacted",
  "metric": "DeltaH",
  "before": {
    "run_id": "exp_001_synthetic_generated_before",
    "score": 4.0,
    "report": "reports/local/exp_001_synthetic_generated_before.md"
  },
  "after": {
    "run_id": "exp_001_synthetic_generated_after",
    "score": 1.0,
    "report": "reports/local/exp_001_synthetic_generated_after.md"
  },
  "delta": 3.0,
  "status": "reduced"
}
```

## Validate

```bash
python scripts/validate_patch_verification.py examples/synthetic/patch_verification_sample.json
```

JSON summary:

```bash
python scripts/validate_patch_verification.py --json examples/synthetic/patch_verification_sample.json
```

## Required Fields

| Field | Meaning |
|---|---|
| `verification_id` | Stable verification identifier |
| `target` | Target name |
| `view` | Public-safe trace view |
| `metric` | Metric being compared |
| `before` | Before-patch measurement |
| `after` | After-patch measurement |
| `status` | Comparison status |

## Status Values

| Status | Meaning |
|---|---|
| `reduced` | Score decreased after the change |
| `unchanged` | Score stayed within tolerance |
| `increased` | Score increased after the change |
| `inconclusive` | Result cannot support a directional claim |

## Claim Level

Patch verification supports the path toward L5 claims, but only when combined with:

- repeated runs;
- stable measurement conditions;
- public-safe reports;
- clear before/after source change description;
- no raw or secret-equivalent public data.
