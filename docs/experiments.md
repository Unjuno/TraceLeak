# Experiment Configuration

TraceLeak experiment configs record which files and metrics belong to a run.

The config layer does not execute heavy jobs. It only validates metadata for repeatable lightweight workflows.

## Purpose

```text
config
  -> validate_config.py
  -> trace validation
  -> feature extraction
  -> baseline evaluation
  -> report generation
```

## Example Config

```json
{
  "experiment_id": "exp_000_synthetic_leak",
  "experiment_type": "synthetic",
  "target": "synthetic-example",
  "view": "redacted",
  "metric": "DeltaH",
  "inputs": {
    "trace": "examples/synthetic/synthetic_trace_sample.jsonl",
    "ablation": "examples/synthetic/ablation_sample.json",
    "baseline": "examples/synthetic/baseline_sample.json"
  },
  "outputs": {
    "report_md": "reports/local/exp_000_synthetic_leak.md",
    "report_json": "reports/local/exp_000_synthetic_leak.json"
  },
  "safety": {
    "contains_raw_trace": false,
    "contains_secret_equivalent": false,
    "public_safe": true
  }
}
```

## Validate Configs

```bash
python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json
```

PowerShell:

```powershell
python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json
```

JSON summary:

```bash
python scripts/validate_config.py --json experiments/exp_000_synthetic_leak/config.json
```

## Fields

| Field | Required | Meaning |
|---|---:|---|
| `experiment_id` | yes | Stable experiment identifier |
| `experiment_type` | yes | `synthetic`, `toy-rsa`, `openssl-rsa-keygen`, `baseline`, or `reporting` |
| `target` | yes | Target implementation or example |
| `view` | yes | Trace view |
| `metric` | yes | Metric name |
| `inputs` | yes | Input file paths |
| `outputs` | no | Output file paths |
| `safety` | no | Safety flags |
| `notes` | no | Human-readable notes |

## Recommended Lightweight Flow

```bash
python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json
python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl
python scripts/extract_features.py --in examples/synthetic/synthetic_trace_sample.jsonl --out features.json
python scripts/evaluate_baseline.py --in examples/synthetic/baseline_sample.json
python scripts/make_report.py --in examples/synthetic/ablation_sample.json --out report.md
```

Generated local files such as `features.json`, `report.md`, and `report.json` are ignored by default.
