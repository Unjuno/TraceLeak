# Reporting Workflow

TraceLeak separates heavy local experiments from lightweight report generation.

The expected workflow is:

```text
local experiment
  -> ablation result JSON
  -> scripts/make_report.py
  -> Markdown or JSON report
```

The report generator does not train models and does not inspect raw traces. It consumes already-computed local metrics.

## Input Format

```json
{
  "target": "synthetic-example",
  "view": "redacted",
  "metric": "DeltaH",
  "full_score": 10.0,
  "groups": {
    "example_branch_event": {
      "ablated_score": 4.0,
      "group_type": "branch",
      "location": "examples/synthetic/target.c:21"
    }
  },
  "notes": ["Synthetic sample for validating report generation."]
}
```

Fields:

| Field | Meaning |
|---|---|
| `target` | Experiment target name |
| `view` | Trace view used for the measurement |
| `metric` | Metric name, usually `DeltaH` |
| `full_score` | Score from the full feature set |
| `groups` | Ablated source-level groups |
| `ablated_score` | Score after removing that group |
| `group_type` | Variable, branch, loop, phase, function, file, or mixed |
| `location` | Optional source location |
| `notes` | Optional report notes |

## Contribution Score

For each group `j`, TraceLeak computes:

```text
s_j = full_score - ablated_score_j
```

For DeltaH experiments:

```text
s_j = DeltaH(X) - DeltaH(X_without_j)
```

A larger positive value means that removing the group reduced measured leakage more strongly.

Small negative values may occur because local measurements can be noisy.

## Generate Markdown

```bash
python scripts/make_report.py \
  --in examples/synthetic/ablation_sample.json \
  --out report.md
```

PowerShell:

```powershell
python scripts/make_report.py --in examples/synthetic/ablation_sample.json --out report.md
```

## Generate JSON

```bash
python scripts/make_report.py \
  --in examples/synthetic/ablation_sample.json \
  --out report.json \
  --format json
```

PowerShell:

```powershell
python scripts/make_report.py --in examples/synthetic/ablation_sample.json --out report.json --format json
```

## Local Output Policy

Local generated reports are ignored by default when they are written to:

```text
/report.md
/report.json
reports/local/
*.local.md
*.local.json
```

Reports intended for public examples should be placed under `examples/` and must not include raw traces, private keys, RNG state, DRBG state, or secret-equivalent material.

## Claim Discipline

Reports should preserve TraceLeak's claim boundary:

- raw-only results are upper-bound measurements;
- redacted/path/observable results are stronger;
- source-localized results are stronger still;
- patch-verified results are the strongest.

A report must not frame raw internal-value measurements as real-world exploitability.
