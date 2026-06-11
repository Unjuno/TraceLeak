# Model Result Files

Model result files connect local modeling to TraceLeak's public-safe reporting workflow.

They are intended to contain metrics and source-level attribution summaries. They must not contain raw traces, private values, model checkpoints, or secret-equivalent material.

## Purpose

```text
local model training
  -> model result JSON
  -> validate_model_result.py
  -> model_result_to_report.py
  -> attribution report
```

The repository does not run neural training by default. Local model outputs can be imported later through this stable JSON shape.

## Example

```json
{
  "experiment_id": "exp_001_synthetic_generated",
  "target": "synthetic-leak",
  "view": "redacted",
  "model": {
    "name": "local-neural-placeholder",
    "type": "neural",
    "version": "local"
  },
  "metrics": {
    "test": {
      "accuracy": 0.875,
      "DeltaH": 4.0,
      "top_k_recall": 1.0
    }
  },
  "attributions": [
    {
      "group_id": "synthetic_branch_event",
      "group_type": "branch",
      "score": 3.0,
      "location": "examples/synthetic/target.py:19",
      "evidence": ["model_importance", "ablation"]
    }
  ]
}
```

## Validate

```bash
python scripts/validate_model_result.py examples/synthetic/model_result_sample.json
```

PowerShell:

```powershell
python scripts/validate_model_result.py examples/synthetic/model_result_sample.json
```

JSON summary:

```bash
python scripts/validate_model_result.py --json examples/synthetic/model_result_sample.json
```

## Convert to Report

Markdown report:

```bash
python scripts/model_result_to_report.py --in examples/synthetic/model_result_sample.json --out model_report.md
```

JSON report:

```bash
python scripts/model_result_to_report.py --in examples/synthetic/model_result_sample.json --out model_report.json --format json
```

Select a different metric:

```bash
python scripts/model_result_to_report.py --in examples/synthetic/model_result_sample.json --out accuracy_report.md --metric accuracy
```

## Required Fields

| Field | Meaning |
|---|---|
| `experiment_id` | Experiment identifier |
| `target` | Target name |
| `view` | Public-safe trace view |
| `model` | Model metadata |
| `metrics` | Split-level metric values |

## Optional Fields

| Field | Meaning |
|---|---|
| `attributions` | Source-level model attribution rows |
| `notes` | Human-readable notes |

## Public-Safe Rule

By default, validation rejects non-public-safe views and secret-equivalent field names.

Use `--allow-raw` only for local lab files that will not be committed.
